import json
import os
from typing import Any, Optional

import boto3

from quant_core.broker.data_broker import DataBroker
from quant_core.clients.ig.ig_api import IGApi, IGApiPostPositionsOrderBody, IGApiPostWorkingOrderBody
from quant_core.enums.ig.time_in_force import TimeInForce
from quant_core.enums.order_type import OrderType
from quant_core.enums.trade_direction import TradeDirection
from quant_core.services.core_logger import CoreLogger
from quant_core.trader.trader import Trader


class IgTrader(Trader):
    def __init__(
        self,
        secret_id: str,
    ) -> None:
        user_name, password, api_key, account_id = self._get_ig_credentials(secret_id)
        self._api: IGApi = IGApi(
            user_name=user_name,
            password=password,
            api_key=api_key,
            account_id=account_id,
        )

    def _get_ig_credentials(self, secret_id: str) -> tuple[str, str, str, str]:
        """
        Retrieve IG credentials from secrets manager.
        """
        # Assuming the secret_id is used to fetch the credentials from a secrets manager
        # This part of the code is not provided in the original snippet
        secrets_manager = boto3.client("secretsmanager", region_name="eu-west-1")
        secret = secrets_manager.get_secret_value(SecretId=secret_id)
        secret_dict = json.loads(secret["SecretString"])
        user_name = secret_dict.get("IG_USERNAME")
        password = secret_dict.get("IG_PASSWORD")
        api_key = secret_dict.get("IG_API_KEY")
        account_id = secret_dict.get("IG_ACCOUNT_ID")
        if not all([user_name, password, api_key, account_id]):
            raise ValueError("Missing IG credentials in secrets manager.")

        return user_name, password, api_key, account_id

    def get_balance(self) -> float:
        accounts = self._api.get_accounts()
        if not accounts:
            CoreLogger().error("No accounts found.")
            raise ValueError("No accounts found.")

        account_id = os.environ.get("IG_ACCOUNT_ID")
        account = [account for account in accounts if account.account_id == account_id][0]

        if not account:
            CoreLogger().error(f"No account found with ID: {account_id}")
            raise ValueError(f"No account found with ID: {account_id}")

        return account.balance["balance"]

    def open_position(
        self,
        symbol: str,
        trade_direction: TradeDirection,
        order_type: OrderType,
        size: float,
        stop_loss: float,
        take_profit: float,
        limit_level: Optional[float] = None,
    ) -> Any:
        currency_code = DataBroker().convert_epic_to_polygon(symbol)[-3:]
        if order_type is OrderType.MARKET:
            CoreLogger().info(f"Opening Market position: {trade_direction} {size} {stop_loss} {take_profit}")
            return self._api.post_positions_otc(
                IGApiPostPositionsOrderBody(
                    currency_code=currency_code,
                    direction=trade_direction.value,
                    epic=symbol,
                    expiry="-",
                    force_open=True,
                    guaranteed_stop=False,
                    size=size,
                    order_type=order_type.value,
                    time_in_force=TimeInForce.EXECUTE_AND_ELIMINATE,
                    limit_level=take_profit,
                    stop_level=stop_loss,
                    trailing_stop=False,
                )
            )
        elif order_type is OrderType.LIMIT:
            CoreLogger().info(
                f"Opening Limit position: {trade_direction} {size} SL={stop_loss} TP={take_profit} Entry={limit_level}"
            )
            return self._api.post_working_otc(
                IGApiPostWorkingOrderBody(
                    currency_code=currency_code,
                    direction=trade_direction.value,
                    epic=symbol,
                    expiry="-",
                    force_open=True,
                    guaranteed_stop=False,
                    level=limit_level,
                    order_type=order_type.value,
                    size=size,
                    time_in_force=TimeInForce.GOOD_TILL_CANCELLED,
                    limit_level=take_profit,
                    stop_level=stop_loss,
                )
            )
        else:
            raise NotImplementedError("Only market and limit orders are supported for IG currently.")
