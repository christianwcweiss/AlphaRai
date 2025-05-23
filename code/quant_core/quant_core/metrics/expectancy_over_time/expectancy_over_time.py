import pandas as pd

from quant_core.enums.trade_event_type import TradeEventType
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class ExpectancyOverTime(TradeMetricOverTime):
    """Calculates the expectancy over time for each account."""

    def calculate(
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = True,
        group_by_symbol: bool = False,
        rolling_window: int = 30,
    ) -> pd.DataFrame:
        data_frame = data_frame.copy()
        data_frame["closed_at"] = pd.to_datetime(data_frame["closed_at"])
        data_frame = data_frame[data_frame["profit"].notna()]
        initial_balances = self._get_initial_balances(data_frame)
        if not group_by_account_id and not group_by_symbol:
            data_frame["initial_balance"] = sum(initial_balances.values())
        else:
            data_frame["initial_balance"] = data_frame["account_id"].map(initial_balances, na_action="ignore")

        window_results = []

        groups = self.groups(group_by_account_id=group_by_account_id, group_by_symbol=group_by_symbol)

        for current_day, window_df in self.get_rolling_windows(
            data_frame, skip_head=True, rolling_window=rolling_window
        ).items():
            if group_by_account_id and group_by_symbol:
                grouped = window_df.groupby(groups)
            elif group_by_account_id:
                grouped = window_df.groupby(groups)
            elif group_by_symbol:
                grouped = window_df.groupby(groups)
            else:
                grouped = [((None,), window_df)]

            for group_name, group_df in grouped:
                window_result = self._calculate_group_expectancy(
                    group_df, current_day, group_name, group_by_account_id, group_by_symbol
                )
                window_results.append(window_result)

        return pd.DataFrame(window_results)

    def _calculate_group_expectancy(
        self,
        group_df: pd.DataFrame,
        current_day: pd.Timestamp,
        group_name,
        group_by_account_id: bool,
        group_by_symbol: bool,
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

        if group_by_account_id and group_by_symbol:
            result["account_id"] = group_name[0]
            result["symbol"] = group_name[1]
        elif group_by_account_id:
            result["account_id"] = group_name[0]
        elif group_by_symbol:
            result["symbol"] = group_name[0]

        return result
