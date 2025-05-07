import json
from datetime import datetime, timedelta
from typing import Optional, Any, List
from unittest.mock import Mock

import MetaTrader5 as mt5
import boto3
import pandas as pd

from quant_core.entities.mt5.mt5_trade import CompletedMT5Trade
from quant_core.enums.order_type import OrderType
from quant_core.enums.trade_direction import TradeDirection
from quant_core.services.core_logger import CoreLogger

ORDER_TYPE_MAP = {
    0: "Buy",
    1: "Sell",
    2: "Buy Limit",
    3: "Sell Limit",
    4: "Buy Stop",
    5: "Sell Stop",
    6: "Buy Stop Limit",
    7: "Sell Stop Limit",
}


class Mt5Client:
    def __init__(self, secret_id: str):
        self._secret_id = secret_id
        self._initialized = False
        self._login_to_mt5()

    def _get_mt5_credentials(self) -> tuple[str, str, str]:
        secrets_manager = boto3.client("secretsmanager", region_name="eu-west-1")
        secret = secrets_manager.get_secret_value(SecretId=self._secret_id)
        secret_dict = json.loads(secret["SecretString"])
        login = secret_dict.get("MT5_USER_NAME")
        password = secret_dict.get("MT5_PASSWORD")
        server = secret_dict.get("MT5_SERVER")
        if not all([login, password, server]):
            raise ValueError("Missing MT5 credentials in secrets manager.")
        return login, password, server

    def _login_to_mt5(self) -> None:
        CoreLogger().debug(f"Retrieving MT5 Secrets for secret id {self._secret_id}...")
        login, password, server = self._get_mt5_credentials()
        CoreLogger().debug("Successfully retrieved MT5 Secrets...")

        if isinstance(mt5, Mock):
            CoreLogger().warning("MT5 is mocked. Skipping initialization.")
            self._initialized = False
            return

        if not mt5.initialize():
            CoreLogger().error("MetaTrader5 initialize() failed.")
            return

        authorized = mt5.login(login=int(login), password=password, server=server)
        if not authorized:
            CoreLogger().error(f"MT5 login failed for account: {login}")
            mt5.shutdown()
            return

        CoreLogger().info("MetaTrader5 successfully initialized and logged in.")
        self._initialized = True

    def shutdown(self) -> None:
        if self._initialized:
            mt5.shutdown()
            self._initialized = False
            CoreLogger().info("MetaTrader5 shutdown successful.")

    def get_balance(self) -> float:
        if not self._initialized:
            raise ValueError("MT5 not initialized.")

        account_info = mt5.account_info()
        if account_info is None:
            raise ValueError("Failed to retrieve MT5 account info.")
        return account_info.balance

    def send_order(
        self,
        symbol: str,
        trade_direction: TradeDirection,
        order_type: OrderType,
        size: float,
        stop_loss: float,
        take_profit: float,
        limit_level: Optional[float] = None,
        comment: Optional[str] = None,
    ) -> Any:
        if not self._initialized:
            CoreLogger().error("MT5 is not initialized.")
            return None

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": size,
            "type": trade_direction.to_mt5(order_type=order_type),
            "price": limit_level,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": 10,
            "magic": 234000,
            "comment": comment or "-",
            "type_time": mt5.ORDER_TIME_DAY,
        }

        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            CoreLogger().error(f"MT5 Order failed: {result}")
        return result

    def get_history(self, days: int = 365) -> List[CompletedMT5Trade]:
        """
        Returns a list of CompletedMT5Trade instances for all closed trades in the past X days.
        """
        if not self._initialized:
            raise ValueError("MT5 not initialized.")

        date_from = datetime.now() - timedelta(days=days)
        raw_trades = mt5.history_deals_get(date_from, datetime.now())

        if raw_trades is None:
            CoreLogger().error("❌ Failed to retrieve trade history from MT5.")
            return []

        CoreLogger().info(f"✅ Retrieved {len(raw_trades)} trades from MT5.")

        return [
            CompletedMT5Trade(
                ticket=deal.ticket,
                order=deal.order,
                time=datetime.fromtimestamp(deal.time),
                type_code=deal.type,
                entry_type=deal.entry,
                size=deal.volume,
                symbol=deal.symbol,
                price=deal.price,
                commission=deal.commission,
                swap=deal.swap,
                profit=deal.profit,
                magic=getattr(deal, "magic", None),
                comment=getattr(deal, "comment", None),
            )
            for deal in raw_trades
        ]

    def get_history_df(self, days: int = 365) -> pd.DataFrame:
        """
        Returns a Pandas DataFrame of all closed trades from the last X days.
        """
        return pd.DataFrame(
            [
                {
                    "ticket": t.ticket,
                    "order": t.order,
                    "time": t.time,
                    "type": t.type_code,
                    "entry": t.entry_type,
                    "size": t.size,
                    "symbol": t.symbol,
                    "price": t.price,
                    "commission": t.commission,
                    "swap": t.swap,
                    "profit": t.profit,
                    "magic": t.magic,
                    "comment": t.comment,
                }
                for t in self.get_history(days=days)
            ]
        )

    def get_all_symbols(self) -> list[dict]:
        raw_symbols = mt5.symbols_get()
        if raw_symbols is None:
            raise RuntimeError(f"Failed to fetch symbols: {mt5.last_error()}")

        return [
            {
                "name": s.name,
                "digits": s.digits,
                "lot_size": getattr(s, "trade_contract_size", 1.0),  # ← this
            }
            for s in raw_symbols
        ]