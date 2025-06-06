from typing import Optional

import pandas as pd
from quant_core.enums.trade_event_type import TradeEventType
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class ExpectancyOverTime(TradeMetricOverTime):
    """Calculates the expectancy over time for each account."""

    def calculate(  # pylint: disable=too-many-arguments, too-many-positional-arguments, too-many-locals
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = True,
        group_by_symbol: bool = False,
        group_by_asset_type: bool = False,
        group_by_direction: bool = False,
        group_by_hour: bool = False,
        group_by_weekday: bool = False,
        rolling_window: Optional[int] = 30,
    ) -> pd.DataFrame:
        data_frame = data_frame.copy()

        if not rolling_window:
            rolling_window = 30

        groups = self.groups(
            group_by_account_id=group_by_account_id,
            group_by_symbol=group_by_symbol,
            group_by_asset_type=group_by_asset_type,
            group_by_direction=group_by_direction,
            group_by_hour=group_by_hour,
            group_by_weekday=group_by_weekday,
        )

        data_frame = self._normalize_time(data_frame=data_frame)
        if not all(group in data_frame.columns for group in groups):
            raise ValueError(f"Some group columns are missing in the DataFrame: {groups}")

        self.set_initial_balances(data_frame=data_frame, group_by_account_id=group_by_account_id)

        expectancy_window_results = []
        for current_day, window_df in self.get_rolling_windows(
            data_frame, skip_head=True, rolling_window=rolling_window
        ).items():
            if groups:
                grouped = window_df.groupby(groups)
            else:
                grouped = [((None,), window_df)]

            for group_name, group_df in grouped:
                window_result = self._calculate_group_expectancy(group_df, current_day, groups, group_name)
                expectancy_window_results.append(window_result)

        return pd.DataFrame(expectancy_window_results)

    def _calculate_group_expectancy(
        self,
        group_df: pd.DataFrame,
        current_day: pd.Timestamp,
        group_keys: list[str],
        group_name: tuple,
    ) -> dict:
        group_df = group_df[group_df["event"] != TradeEventType.DEPOSIT.value]
        winning_trades = group_df[group_df["profit"] > 0]
        losing_trades = group_df[group_df["profit"] < 0]

        win_rate = len(winning_trades) / len(group_df) if len(group_df) > 0 else 0.0
        avg_win = winning_trades["profit"].mean() if not winning_trades.empty else 0.0
        avg_loss = abs(losing_trades["profit"].mean()) if not losing_trades.empty else 0.0

        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        initial_balance = group_df["initial_balance"].iloc[0] if not group_df.empty else None

        result = {
            "time": current_day,
            "expectancy": round(expectancy, 2),
            "expectancy_pct": round(expectancy, 2) / initial_balance if initial_balance else 0.0,
        }

        for i, key in enumerate(group_keys):
            result[key] = group_name[i]

        return result
