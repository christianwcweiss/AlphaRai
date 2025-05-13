from abc import ABC, abstractmethod
from typing import Dict, Optional, Literal, List

import pandas as pd

from quant_core.enums.trade_event_type import TradeEventType


class TradeMetricOverTime(ABC):
    """Trade metric over time base class."""

    def _get_initial_balances(self, data_frame: pd.DataFrame) -> Dict[str, float]:
        return (
            data_frame[data_frame["event"] == TradeEventType.DEPOSIT.value]
            .groupby("account_id")["profit"]
            .sum()
            .to_dict()
        )

    @abstractmethod
    def calculate(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = True,
        group_by_symbol: bool = False,
        group_by_asset_type: bool = False,
        group_by_direction: bool = False,
        group_by_hour: bool = False,
        group_by_weekday: bool = False,
        rolling_window: Optional[int] = None,
    ) -> pd.DataFrame:
        """Calculate the metric grouped by account_id."""

    @staticmethod
    def _normalize_time(data_frame: pd.DataFrame) -> pd.DataFrame:
        """Normalize time to a specific resolution."""
        data_frame = data_frame.copy()

        data_frame["opened_at"] = pd.to_datetime(data_frame["opened_at"])
        data_frame["open_hour"] = data_frame["opened_at"].dt.hour
        data_frame["open_weekday"] = data_frame["opened_at"].dt.weekday  # 0 = Monday

        data_frame["closed_at"] = pd.to_datetime(data_frame["closed_at"])
        data_frame["close_hour"] = data_frame["closed_at"].dt.hour
        data_frame["close_weekday"] = data_frame["closed_at"].dt.weekday  # 0 = Monday

        data_frame = data_frame.sort_values("opened_at")

        return data_frame

    @staticmethod
    def groups(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        group_by_account_id: bool,
        group_by_symbol: bool,
        group_by_asset_type: bool,
        group_by_direction: bool,
        group_by_hour: bool,
        group_by_weekday: bool,
    ) -> List[str]:
        """Get the groups for grouping the DataFrame."""
        groups = []
        if group_by_account_id:
            groups.append("account_id")
        if group_by_asset_type:
            groups.append("asset_type")
        if group_by_direction:
            groups.append("direction")
        if group_by_symbol:
            groups.append("symbol")
        if group_by_hour:
            groups.append("open_hour")
        if group_by_weekday:
            groups.append("open_weekday")

        return groups

    def set_initial_balances(self, data_frame: pd.DataFrame, group_by_account_id: bool) -> pd.DataFrame:
        """Set initial balances for each account."""
        data_frame["initial_balance"] = 0.0
        initial_balances = self._get_initial_balances(data_frame)
        if group_by_account_id:
            for account, balance in initial_balances.items():
                data_frame.loc[data_frame["account_id"] == account, "initial_balance"] = balance
        else:
            data_frame["initial_balance"] = sum(initial_balances.values())

        return data_frame

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
            data_frame["agg_time_opened"] = data_frame["opened_at"].dt.normalize()
            data_frame["agg_time_closed"] = data_frame["closed_at"].dt.normalize()
        elif aggregation_resolution == "H":
            data_frame["agg_time_opened"] = data_frame["opened_at"].dt.floor("H")
            data_frame["agg_time_closed"] = data_frame["closed_at"].dt.floor("H")
        else:
            raise ValueError(f"Unsupported aggregation resolution: {aggregation_resolution}")

        start_time = data_frame["agg_time_opened"].min()
        end_time = data_frame["agg_time_closed"].max()

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
            mask = (data_frame["agg_time_closed"] > window_start) & (data_frame["agg_time_closed"] <= window_end)

            result[current_period] = data_frame.loc[mask]

        if skip_head:
            result = {
                k: v for i, (k, v) in enumerate(sorted(result.items(), key=lambda item: item[0])) if i >= rolling_window
            }

        result.pop(pd.NaT, None)

        return result
