from abc import ABC, abstractmethod
from typing import Dict, Optional, Literal

import pandas as pd


class TradeMetricOverTime(ABC):
    """Trade metric over time base class."""

    def _get_initial_balances(self, data_frame: pd.DataFrame) -> Dict[str, float]:
        return data_frame[data_frame["type"] == 2].groupby("account_id")["profit"].sum().to_dict()

    @abstractmethod
    def calculate(
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = True,
        group_by_symbol: bool = False,
        rolling_window_days: Optional[int] = None,
    ) -> pd.DataFrame:
        """Calculate the metric grouped by account_id."""

    @staticmethod
    def _normalize_time(data_frame: pd.DataFrame) -> pd.DataFrame:
        """Normalize time to a specific resolution."""
        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"])
        data_frame = data_frame.sort_values("time")

        return data_frame

    @staticmethod
    def _get_groups(group_by_account_id: bool, group_by_symbol: bool) -> list:
        """Get the groups for grouping the DataFrame."""
        groups = []
        if group_by_account_id:
            groups.append("account_id")
        if group_by_symbol:
            groups.append("symbol")

        return groups

    @staticmethod
    def get_rolling_windows(
        data_frame: pd.DataFrame,
        skip_head: bool = False,
        aggregation_resolution: Literal["D", "H"] = "D",
        rolling_window: int = 30,
    ) -> Dict[pd.Timestamp, pd.DataFrame]:
        """
        Returns a dict of {aggregated_time: trades within the past `rolling_window_days` up to that point}.
        - Supports arbitrary aggregation_resolution (e.g., 'D', 'H')
        - If 'D', truncates timestamps to midnight for consistent grouping
        - Skips first N windows if skip_head=True
        """
        data_frame = data_frame.copy()
        data_frame = TradeMetricOverTime._normalize_time(data_frame)

        if data_frame.empty:
            return {}

        if aggregation_resolution == "D":
            data_frame["agg_time"] = data_frame["time"].dt.normalize()
        elif aggregation_resolution == "H":
            data_frame["agg_time"] = data_frame["time"].dt.floor("H")
        else:
            raise ValueError(f"Unsupported aggregation resolution: {aggregation_resolution}")

        start_time = data_frame["agg_time"].min()
        end_time = data_frame["agg_time"].max()

        all_periods = pd.date_range(start=start_time, end=end_time, freq=aggregation_resolution, inclusive="both")

        result = {}

        for current_period in all_periods:
            delta = (
                pd.Timedelta(days=rolling_window)
                if aggregation_resolution == "D"
                else pd.Timedelta(hours=rolling_window)
            )
            window_start = current_period - delta
            window_end = current_period
            mask = (data_frame["agg_time"] > window_start) & (data_frame["agg_time"] <= window_end)

            result[current_period] = data_frame.loc[mask]

        if skip_head:
            result = {
                k: v for i, (k, v) in enumerate(sorted(result.items(), key=lambda item: item[0])) if i >= rolling_window
            }

        result.pop(pd.NaT, None)

        return result
