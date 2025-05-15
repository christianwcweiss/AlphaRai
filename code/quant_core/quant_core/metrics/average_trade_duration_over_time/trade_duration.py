import pandas as pd
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class AvgTradeDurationOverTime(TradeMetricOverTime):
    """Average Trade Duration Over Time."""

    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if data_frame.empty or "time" not in data_frame.columns or "duration" not in data_frame.columns:
            return pd.DataFrame(columns=["time", "account_id", "result", "avg_duration_min"])

        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"])
        data_frame["result"] = data_frame["profit"].apply(lambda p: "win" if p > 0 else "loss")
        data_frame = data_frame[data_frame["result"].notna()]

        result = []

        for current_day, window_df in self.get_rolling_windows(data_frame, skip_head=True).items():
            for account, group in window_df.groupby("account_id"):
                for result_type, result_group in group.groupby("result"):
                    if result_group.empty:
                        continue

                    avg_duration = result_group["duration"].mean()
                    result.append(
                        {
                            "time": current_day,
                            "account_id": account,
                            "result": result_type,
                            "avg_duration_min": round(avg_duration, 2),
                        }
                    )

        return pd.DataFrame(result)
