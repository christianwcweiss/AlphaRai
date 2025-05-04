import pandas as pd
from quant_core.metrics.trade_metric import TradeMetric

class AvgTradeDurationOverTime(TradeMetric):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "time" not in df.columns or "duration" not in df.columns:
            return pd.DataFrame(columns=["time", "result", "avg_duration_min"])

        df = df.copy()
        df["time"] = pd.to_datetime(df["time"]).dt.date
        df["result"] = df["profit"].apply(lambda p: "win" if p > 0 else "loss")

        grouped = (
            df.groupby(["time", "result"])["duration"]
            .mean()
            .reset_index()
            .rename(columns={"duration": "avg_duration_min"})
        )

        return grouped
