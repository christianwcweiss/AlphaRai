from typing import Optional, Literal

import pandas as pd
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class CommissionOverTime(TradeMetricOverTime):
    """Calculates the total commission over time."""

    def _calculate_comission_in_cum_sum(
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = False,
        group_by_symbol: bool = False,
    ) -> pd.DataFrame:
        groups = self._get_groups(group_by_account_id=group_by_account_id, group_by_symbol=group_by_symbol)

        if groups:
            data_frame["total_commission"] = data_frame.groupby(groups)["commission"].cumsum()
        else:
            data_frame["total_commission"] = data_frame["commission"].cumsum()

        data_frame = data_frame.drop_duplicates(keep="last")

        return data_frame[["time"] + groups + ["total_commission"]]

    def _calculate_comission_in_period_windows(
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = False,
        group_by_symbol: bool = False,
        rolling_window: Optional[int] = 7,
        aggregation_resolution: Literal["D", "H"] = "D",
    ) -> pd.DataFrame:
        rolling_windows = self.get_rolling_windows(
            data_frame=data_frame,
            skip_head=False,
            aggregation_resolution=aggregation_resolution,
            rolling_window=rolling_window if rolling_window else None,
        )

        groups = self._get_groups(group_by_account_id=group_by_account_id, group_by_symbol=group_by_symbol)

        result = []
        for window_time, window_df in rolling_windows.items():
            if groups:
                window_df["total_commission"] = window_df.groupby(groups)["commission"].transform("sum")
            else:
                window_df["total_commission"] = window_df["commission"].sum()

            window_df["time"] = window_time
            window_df = window_df.drop_duplicates(subset=groups + ["time"], keep="last")

            for _, row in window_df.iterrows():
                result.append(row)

        result_df = pd.DataFrame(result)

        return result_df[["time"] + groups + ["total_commission"]]

    def calculate(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = False,
        group_by_symbol: bool = False,
        rolling_window: Optional[int] = 7,
        aggregation_resolution: Literal["D", "H"] = "D",
        cum_sum: bool = False,
    ) -> pd.DataFrame:
        commission_df = self._normalize_time(data_frame)

        if cum_sum:
            result_df = self._calculate_comission_in_cum_sum(
                data_frame=commission_df,
                group_by_account_id=group_by_account_id,
                group_by_symbol=group_by_symbol,
            )
        else:
            result_df = self._calculate_comission_in_period_windows(
                data_frame=commission_df,
                group_by_account_id=group_by_account_id,
                group_by_symbol=group_by_symbol,
                rolling_window=rolling_window,
                aggregation_resolution=aggregation_resolution,
            )

        return result_df
