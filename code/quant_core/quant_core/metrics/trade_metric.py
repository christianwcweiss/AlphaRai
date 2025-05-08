from abc import ABC, abstractmethod
from typing import Dict, List

import pandas as pd


class TradeMetricOverTime(ABC):
    def __init__(self, rolling_window_days: int = 30) -> None:
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

    def get_rolling_windows(self, df: pd.DataFrame, skip_head: bool = False) -> Dict[pd.Timestamp, pd.DataFrame]:
        """
        Returns a dict of {date: trades within the past `rolling_window_days` including that date}.
        - Includes all calendar dates (via pd.date_range)
        - Skips the first N days if `skip_head=True` (to ensure full window)
        """
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df = df.sort_values("time")

        if df.empty:
            return {}

        start_date = df["time"].min().normalize()
        end_date = df["time"].max().normalize()

        # Create full date range (even if no trades)
        all_days = pd.date_range(start=start_date, end=end_date, freq="D")

        if skip_head:
            all_days = all_days[self.rolling_window_days :]

        result = {}

        for current_day in all_days:
            window_start = current_day - pd.Timedelta(days=self.rolling_window_days)
            mask = (df["time"] > window_start) & (df["time"] <= current_day)
            result[current_day.date()] = df.loc[mask]

        return result
