# pylint: disable=no-member
import json
from collections import defaultdict
from datetime import datetime, timedelta
from random import randint
from typing import Any, List, Optional
from unittest.mock import Mock

import boto3
import pandas as pd
from quant_core.entities.dto.trade import AlphaTradeDTO
from quant_core.entities.mt5.mt5_symbol import MT5Symbol
from quant_core.entities.mt5.mt5_trade import CompletedMT5Trade
from quant_core.enums.order_type import OrderType
from quant_core.enums.trade_direction import TradeDirection
from quant_core.enums.trade_event_type import TradeEventType
from quant_core.services.core_logger import CoreLogger

try:
    import MetaTrader5 as mt5
except ImportError:
    from quant_core.mock import mt5


class Mt5Client:
    """A client for interacting with MetaTrader 5."""

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

        if not mt5.initialize():  # type: ignore
            CoreLogger().error("MetaTrader5 initialize() failed.")
            return

        authorized = mt5.login(login=int(login), password=password, server=server)  # type: ignore
        if not authorized:
            CoreLogger().error(f"MT5 login failed for account: {login}")
            mt5.shutdown()  # type: ignore
            return

        CoreLogger().info("MetaTrader5 successfully initialized and logged in.")
        self._initialized = True

    def shutdown(self) -> None:
        """Shutdown the MT5 client."""
        if self._initialized:
            mt5.shutdown()
            self._initialized = False
            CoreLogger().info("MetaTrader5 shutdown successful.")

    def get_balance(self) -> float:
        """Get the current balance from MT5."""
        if not self._initialized:
            raise ValueError("MT5 not initialized.")

        account_info = mt5.account_info()  # type: ignore
        if account_info is None:
            raise ValueError("Failed to retrieve MT5 account info.")
        return account_info.balance

    def send_order(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        symbol: str,
        trade_direction: TradeDirection,
        order_type: OrderType,
        size: float,
        stop_loss: float,
        take_profit: float,
        magic: Optional[int] = None,
        limit_level: Optional[float] = None,
        comment: Optional[str] = None,
    ) -> Any:
        """Sends an order to MT5."""
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
            "magic": magic or randint(100000, 999999),
            "comment": comment or "-",
            "type_time": mt5.ORDER_TIME_DAY,
        }

        result = mt5.order_send(request)  # type: ignore
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
        date_to = datetime.now() + timedelta(days=1)
        raw_trades = mt5.history_deals_get(date_from, date_to)  # type: ignore

        if raw_trades is None:
            CoreLogger().error("Failed to retrieve trade history from MT5.")
            return []

        CoreLogger().info(f"Retrieved {len(raw_trades)} trades from MT5.")

        return [
            CompletedMT5Trade(
                position_id=deal.position_id,
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
                    "id": t.position_id,
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

    def get_history_alpha_trades(self, account_id: str, days: int = 365) -> List[AlphaTradeDTO]:
        """
        Returns a list of AlphaTradeDTO instances for all closed trades in the past X days.
        """
        mt5_trades = sorted(self.get_history(days=days), key=lambda x: x.time)
        default_dict_dp = defaultdict(list)
        result = []

        for trade in mt5_trades:
            if trade.type_code == 2 and trade.entry_type == 0 and not trade.symbol:
                result.append(
                    AlphaTradeDTO(
                        id=trade.position_id,
                        account_id=account_id,
                        order=trade.ticket,
                        trade_group="-",
                        opened_at=trade.time,
                        closed_at=trade.time,
                        direction=TradeDirection.NEUTRAL,
                        event=TradeEventType.DEPOSIT,
                        size=trade.size,
                        symbol=trade.symbol,
                        entry_price=0.0,
                        exit_price=0.0,
                        profit=trade.profit,
                        swap=trade.swap,
                        commission=trade.commission,
                    )
                )
            else:
                default_dict_dp[trade.position_id].append(trade)
                if len(default_dict_dp[trade.position_id]) == 2:
                    opened_trade = default_dict_dp[trade.position_id][0]
                    closed_trade = default_dict_dp[trade.position_id][1]
                    direction = TradeDirection.LONG if opened_trade.type_code == 0 else TradeDirection.SHORT
                    result.append(
                        AlphaTradeDTO(
                            id=opened_trade.position_id,
                            account_id=account_id,
                            order=opened_trade.ticket,
                            trade_group=f"{opened_trade.magic}",
                            opened_at=opened_trade.time,
                            closed_at=closed_trade.time,
                            direction=direction,
                            event=TradeEventType.LONG if direction is TradeDirection.LONG else TradeEventType.SHORT,
                            size=opened_trade.size,
                            symbol=opened_trade.symbol,
                            entry_price=opened_trade.price,
                            exit_price=closed_trade.price,
                            profit=opened_trade.profit + closed_trade.profit,
                            swap=opened_trade.swap + closed_trade.swap,
                            commission=closed_trade.commission + opened_trade.commission,
                        )
                    )
                    del default_dict_dp[trade.position_id]

        for trades in default_dict_dp.values():
            if len(trades) == 1:
                opened_trade = trades[0]
                direction = TradeDirection.LONG if opened_trade.type_code == 0 else TradeDirection.SHORT
                result.append(
                    AlphaTradeDTO(
                        id=opened_trade.position_id,
                        account_id=account_id,
                        order=opened_trade.ticket,
                        trade_group=f"{opened_trade.magic}",
                        opened_at=opened_trade.time,
                        closed_at=opened_trade.time,
                        direction=direction,
                        event=TradeEventType.LONG if direction is TradeDirection.LONG else TradeEventType.SHORT,
                        size=opened_trade.size,
                        symbol=opened_trade.symbol,
                        entry_price=0.0,
                        exit_price=0.0,
                        profit=opened_trade.profit,
                        swap=opened_trade.swap,
                        commission=opened_trade.commission,
                    )
                )

        return result

    def get_all_symbols(self) -> List[MT5Symbol]:
        """Get all symbols from MT5."""
        raw_symbols = mt5.symbols_get()
        if raw_symbols is None:
            raise RuntimeError(f"Failed to fetch symbols: {mt5.last_error()}")

        symbols = []
        for symbol in raw_symbols:
            symbols.append(
                MT5Symbol(
                    is_custom=symbol.custom,
                    chart_mode=symbol.chart_mode,
                    select=symbol.select,
                    visible=symbol.visible,
                    session_deals=symbol.session_deals,
                    session_buy_orders=symbol.session_buy_orders,
                    session_sell_orders=symbol.session_sell_orders,
                    volume=symbol.volume,
                    volume_high=symbol.volumehigh,
                    volume_low=symbol.volumelow,
                    time=symbol.time,
                    digits=symbol.digits,
                    spread=symbol.spread,
                    spread_float=symbol.spread_float,
                    ticks_bookdepth=symbol.ticks_bookdepth,
                    trade_calc_mode=symbol.trade_calc_mode,
                    trade_mode=symbol.trade_mode,
                    start_time=symbol.start_time,
                    expiration_time=symbol.expiration_time,
                    trade_stops_level=symbol.trade_stops_level,
                    trade_freeze_level=symbol.trade_freeze_level,
                    trade_exemode=symbol.trade_exemode,
                    swap_mode=symbol.swap_mode,
                    swap_rollover3days=symbol.swap_rollover3days,
                    margin_hedged_use_leg=symbol.margin_hedged_use_leg,
                    expiration_mode=symbol.expiration_mode,
                    filling_mode=symbol.filling_mode,
                    order_mode=symbol.order_mode,
                    order_gtc_mode=symbol.order_gtc_mode,
                    option_mode=symbol.option_mode,
                    option_right=symbol.option_right,
                    bid=symbol.bid,
                    bidhigh=symbol.bidhigh,
                    bidlow=symbol.bidlow,
                    ask=symbol.ask,
                    askhigh=symbol.askhigh,
                    asklow=symbol.asklow,
                    last=symbol.last,
                    lasthigh=symbol.lasthigh,
                    lastlow=symbol.lastlow,
                    volume_real=symbol.volume_real,
                    volumehigh_real=symbol.volumehigh_real,
                    volumelow_real=symbol.volumelow_real,
                    option_strike=symbol.option_strike,
                    point=symbol.point,
                    trade_tick_value=symbol.trade_tick_value,
                    trade_tick_value_profit=symbol.trade_tick_value_profit,
                    trade_tick_value_loss=symbol.trade_tick_value_loss,
                    trade_contract_size=symbol.trade_contract_size,
                    trade_accrued_interest=symbol.trade_accrued_interest,
                    trade_face_value=symbol.trade_face_value,
                    trade_liquidity_rate=symbol.trade_liquidity_rate,
                    volume_min=symbol.volume_min,
                    volume_max=symbol.volume_max,
                    volume_step=symbol.volume_step,
                    volume_limit=symbol.volume_limit,
                    swap_long=symbol.swap_long,
                    swap_short=symbol.swap_short,
                    margin_initial=symbol.margin_initial,
                    margin_maintenance=symbol.margin_maintenance,
                    session_volume=symbol.session_volume,
                    session_turnover=symbol.session_turnover,
                    session_interest=symbol.session_interest,
                    session_buy_orders_volume=symbol.session_buy_orders_volume,
                    session_sell_orders_volume=symbol.session_sell_orders_volume,
                    session_open=symbol.session_open,
                    session_close=symbol.session_close,
                    session_aw=symbol.session_aw,
                    session_price_settlement=symbol.session_price_settlement,
                    session_price_limit_min=symbol.session_price_limit_min,
                    session_price_limit_max=symbol.session_price_limit_max,
                    margin_hedged=symbol.margin_hedged,
                    price_change=symbol.price_change,
                    price_volatility=symbol.price_volatility,
                    price_theoretical=symbol.price_theoretical,
                    price_greeks_delta=symbol.price_greeks_delta,
                    price_greeks_theta=symbol.price_greeks_theta,
                    price_greeks_gamma=symbol.price_greeks_gamma,
                    price_greeks_vega=symbol.price_greeks_vega,
                    price_greeks_rho=symbol.price_greeks_rho,
                    price_greeks_omega=symbol.price_greeks_omega,
                    price_sensitivity=symbol.price_sensitivity,
                    basis=symbol.basis,
                    category=symbol.category,
                    currency_base=symbol.currency_base,
                    currency_profit=symbol.currency_profit,
                    currency_margin=symbol.currency_margin,
                    bank=symbol.bank,
                    description=symbol.description,
                    exchange=symbol.exchange,
                    formula=symbol.formula,
                    isin=symbol.isin,
                    name=symbol.name,
                    page=symbol.page,
                    path=symbol.path,
                )
            )

        return symbols
