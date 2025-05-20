from typing import Optional

import pandas as pd

from quant_core.enums.trade_event_type import TradeEventType
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime
from quant_core.services.core_logger import CoreLogger


class AccountBalanceOverTime(TradeMetricOverTime):
    """Account Balance Over Time (Absolute Value)."""

    def calculate(
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = True,
        group_by_symbol: bool = False,
        group_by_hour: bool = False,
        group_by_weekday: bool = False,
        rolling_window: Optional[int] = 1,
    ) -> pd.DataFrame:
        if rolling_window != 1:
            CoreLogger().warning("Rolling window days is not supported for the Account Balance Metric. Ignoring it.")

        balance_df = self._normalize_time(data_frame)
        balance_df["net"] = balance_df["profit"] + balance_df["commission"] + balance_df["swap"]

        balance_df["initial_balance"] = 0.0
        initial_balances = self._get_initial_balances(balance_df)
        if group_by_account_id:
            for account, balance in initial_balances.items():
                balance_df.loc[balance_df["account_id"] == account, "initial_balance"] = balance
        else:
            balance_df["initial_balance"] = sum(initial_balances.values())

        groups = self._get_groups(group_by_account_id=group_by_account_id, group_by_symbol=group_by_symbol, group_by_hour=group_by_hour, group_by_weekday=group_by_weekday)
        balance_df = balance_df.sort_values(by=["account_id", "closed_at"]).reset_index(drop=True)

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

        return balance_df[["closed_at"] + groups + ["initial_balance", "absolute_balance", "initial_balance_pct", "relative_balance"]]
