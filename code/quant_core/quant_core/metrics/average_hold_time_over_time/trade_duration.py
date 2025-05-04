import pandas as pd
from quant_core.metrics.trade_metric import TradeMetric

class AvgHoldTimeOverTime(TradeMetric):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "time" not in df.columns or "duration" not in df.columns:
            return pd.DataFrame(columns=["time", "avg_hold_min"])

        df = df.copy()
        df["time"] = pd.to_datetime(df["time"]).dt.date
        grouped = df.groupby("time")["duration"].mean().reset_index()
        return grouped.rename(columns={"duration": "avg_hold_min"})
