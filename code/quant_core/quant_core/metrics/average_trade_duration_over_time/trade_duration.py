import pandas as pd
from quant_core.metrics.trade_metric import TradeMetricOverTime


class AvgTradeDurationOverTime(TradeMetricOverTime):
    def calculate_grouped(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "time" not in df.columns or "duration" not in df.columns:
            return pd.DataFrame(columns=["time", "account_id", "result", "avg_duration_min"])

        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df["result"] = df["profit"].apply(lambda p: "win" if p > 0 else "loss")
        df = df[df["result"].notna()]

        result = []

        for current_day, window_df in self.get_rolling_windows(df, skip_head=True).items():
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
