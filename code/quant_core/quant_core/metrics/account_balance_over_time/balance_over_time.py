from typing import Optional

import pandas as pd
from quant_core.enums.trade_direction import TradeDirection
from quant_core.enums.trade_event_type import TradeEventType
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime
from quant_core.services.core_logger import CoreLogger


class AccountBalanceOverTime(TradeMetricOverTime):
    """Account Balance Over Time (Absolute Value)."""

    def calculate(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = True,
        group_by_symbol: bool = False,
        group_by_asset_type: bool = False,
        group_by_direction: bool = False,
        group_by_hour: bool = False,
        group_by_weekday: bool = False,
        rolling_window: Optional[int] = 1,
    ) -> pd.DataFrame:
        if rolling_window != 1:
            CoreLogger().warning("Rolling window days is not supported for the Account Balance Metric. Ignoring it.")

        groups = self.groups(
            group_by_account_id=group_by_account_id,
            group_by_symbol=group_by_symbol,
            group_by_asset_type=group_by_asset_type,
            group_by_direction=group_by_direction,
            group_by_hour=group_by_hour,
            group_by_weekday=group_by_weekday,
        )
        balance_df = self._normalize_time(data_frame)

        if not all(group in balance_df.columns for group in groups):
            raise ValueError(f"Some group columns are missing in the DataFrame: {groups}")

        balance_df = self.set_initial_balances(balance_df, group_by_account_id)

        balance_df["net"] = balance_df["profit"] + balance_df["commission"] + balance_df["swap"]
        balance_df = balance_df.sort_values(by=["account_id", "closed_at"]).reset_index(drop=True)
        balance_df = balance_df[balance_df["direction"] != TradeDirection.NEUTRAL.value]

        if groups:
            balance_df["cumulative_net"] = (
                balance_df.where(balance_df["event"] != TradeEventType.DEPOSIT.value)
                .groupby(groups)["net"]
                .cumsum()
                .fillna(0.0)
            )
            balance_df["absolute_balance"] = balance_df["initial_balance"] + balance_df["cumulative_net"]
        else:
            balance_df["absolute_balance"] = (
                balance_df["initial_balance"]
                + balance_df.where(balance_df["event"] != TradeEventType.DEPOSIT.value)["net"].cumsum()
            )
        balance_df["relative_balance"] = (
            1 + (balance_df["absolute_balance"] - balance_df["initial_balance"]) / balance_df["initial_balance"]
        ) * 100
        balance_df["initial_balance_pct"] = 100

        balance_df.sort_values("closed_at", inplace=True)

        return balance_df[
            ["closed_at"] + groups + ["initial_balance", "absolute_balance", "initial_balance_pct", "relative_balance"]
        ]
