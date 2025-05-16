from typing import Optional

import pandas as pd

from quant_core.metrics.account_balance_over_time.absolute.balance_over_time import AccountBalanceOverTimeAbsolute
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class AccountBalanceOverTimeRelative(TradeMetricOverTime):
    """Account balance over time metric (relative)."""

    def calculate(
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = True,
        group_by_symbol: bool = False,
        rolling_window_days: Optional[int] = 1,
    ) -> pd.DataFrame:
        balance_df = data_frame.copy()

        balance_df = AccountBalanceOverTimeAbsolute().calculate(
            data_frame=balance_df,
            group_by_account_id=group_by_account_id,
            group_by_symbol=group_by_symbol,
            rolling_window_days=rolling_window_days,
        )

        balance_df["relative_balance"] = (
            1 + (balance_df["absolute_balance"] - balance_df["initial_balance"]) / balance_df["initial_balance"]
        ) * 100
        balance_df["initial_balance"] = 100

        return balance_df[balance_df.columns.difference(["absolute_balance"])]
