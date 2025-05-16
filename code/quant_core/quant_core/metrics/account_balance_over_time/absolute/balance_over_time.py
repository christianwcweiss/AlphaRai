from typing import Optional

import pandas as pd
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime
from quant_core.services.core_logger import CoreLogger


class AccountBalanceOverTimeAbsolute(TradeMetricOverTime):
    """Account Balance Over Time (Absolute Value)."""

    def calculate(
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = True,
        group_by_symbol: bool = False,
        rolling_window_days: Optional[int] = 1,
    ) -> pd.DataFrame:
        if rolling_window_days != 1:
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

        groups = self._get_groups(group_by_account_id=group_by_account_id, group_by_symbol=group_by_symbol)

        if groups:
            balance_df["initial_balance"] = balance_df.groupby(groups)["initial_balance"].transform("max")
            balance_df["cumulative_net"] = (
                balance_df.where(balance_df["type"] != 2).groupby(groups)["net"].cumsum().fillna(0.0)
            )
            balance_df["absolute_balance"] = balance_df["initial_balance"] + balance_df["cumulative_net"]
        else:
            balance_df["absolute_balance"] = (
                balance_df["initial_balance"] + balance_df.where(balance_df["type"] != 2)["net"].cumsum()
            )

        return balance_df[["time"] + groups + ["initial_balance", "absolute_balance"]]
