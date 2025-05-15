import pandas as pd
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class AvgHoldTimeOverTime(TradeMetricOverTime):
    """Calculates the average hold time of trades over time."""

    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if data_frame.empty or "time" not in data_frame.columns or "duration" not in data_frame.columns:
            return pd.DataFrame(columns=["time", "account_id", "hold_time"])

        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"])
        result = []

        for current_day, window_df in self.get_rolling_windows(data_frame, skip_head=True).items():
            for account, group in window_df.groupby("account_id"):
                if group.empty:
                    continue

                avg_duration = group["duration"].mean()
                result.append(
                    {
                        "time": current_day,
                        "account_id": account,
                        "hold_time": round(avg_duration, 2),
                    }
                )

        return pd.DataFrame(result)
