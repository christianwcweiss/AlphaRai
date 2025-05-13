from abc import ABC, abstractmethod
from typing import Dict, List

import pandas as pd


class TradeMetricOverTime(ABC):
    def __init__(self, rolling_window_days: int = 5) -> None:
        self.rolling_window_days = rolling_window_days

    def _normalize_time(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"]).dt.date
        return df

    def _get_initial_balances(self, data_frame: pd.DataFrame) -> Dict[str, float]:
        return data_frame[data_frame["type"] == 2].groupby("account_id")["profit"].first().to_dict()

    def apply_rolling(self, df: pd.DataFrame, value_cols: List[str]) -> pd.DataFrame:
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df = df.set_index("time").sort_index()

        for col in value_cols:
            df[col] = df[col].rolling(f"{self.rolling_window_days}D").mean()

        return df.reset_index()

    @abstractmethod
    def calculate_grouped(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        pass

    def calculate_ungrouped(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        grouped = self.calculate_grouped(data_frame)
        metric_cols = [col for col in grouped.columns if col not in ["time", "account_id"]]

        return grouped.groupby("time")[metric_cols].mean().reset_index()

    def get_rolling_windows(
            self,
            df: pd.DataFrame,
            skip_head: bool = False,
            aggregation_resolution: str = "D"
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

        # Truncate timestamps to daily resolution if requested
        if aggregation_resolution == "D":
            df["agg_time"] = df["time"].dt.normalize()
        else:
            # General fallback using to_period and back to timestamp
            df["agg_time"] = df["time"].dt.to_period(aggregation_resolution).dt.to_timestamp()

        start_time = df["agg_time"].min()
        end_time = df["agg_time"].max()

        all_periods = pd.date_range(start=start_time, end=end_time, freq=aggregation_resolution)

        if skip_head:
            all_periods = all_periods[self.rolling_window_days:]

        result = {}

        for current_period in all_periods:
            window_start = current_period - pd.Timedelta(days=self.rolling_window_days)
            mask = (df["time"] > window_start) & (df["time"] <= current_period)
            result[current_period] = df.loc[mask]

        return result
