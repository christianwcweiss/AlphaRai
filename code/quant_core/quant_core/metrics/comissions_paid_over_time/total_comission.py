import pandas as pd
from quant_core.metrics.trade_metric import TradeMetric

class CommissionOverTime(TradeMetric):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "commission" not in df.columns or "time" not in df.columns:
            return pd.DataFrame(columns=["time", "commission"])

        df = df.copy()
        df["time"] = pd.to_datetime(df["time"]).dt.date

        return (
            df.groupby("time")["commission"]
            .sum()
            .reset_index()
        )
