from abc import ABC, abstractmethod
from typing import Dict, Optional

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
    def get_rolling_windows(
        df: pd.DataFrame, skip_head: bool = False, aggregation_resolution: str = "D", rolling_window_days: int = 30
    ) -> Dict[pd.Timestamp, pd.DataFrame]:
        """
        Returns a dict of {aggregated_time: trades within the past `rolling_window_days` up to that point}.
        - Supports arbitrary aggregation_resolution (e.g., 'D', 'H', 'W')
        - If 'D', truncates timestamps to midnight for consistent grouping
        - Skips first N windows if skip_head=True
        """
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df = df.sort_values("time")

        if df.empty:
            return {}

        if aggregation_resolution == "D":
            df["agg_time"] = df["time"].dt.normalize()
        else:
            df["agg_time"] = df["time"].dt.to_period(aggregation_resolution).dt.to_timestamp()

        start_time = df["agg_time"].min()
        end_time = df["agg_time"].max()

        all_periods = pd.date_range(start=start_time, end=end_time, freq=aggregation_resolution)

        result = {}

        for current_period in all_periods:
            window_start = current_period - pd.Timedelta(days=rolling_window_days)
            mask = (df["time"] > window_start) & (df["time"] <= current_period)
            result[current_period] = df.loc[mask]

        if skip_head:
            result = {
                k: v
                for i, (k, v) in enumerate(sorted(result.items(), key=lambda item: item[0]))
                if rolling_window_days > i
            }

        return result
