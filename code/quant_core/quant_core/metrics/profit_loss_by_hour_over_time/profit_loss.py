import pandas as pd
from quant_core.metrics.trade_metric import TradeMetric

class ProfitByHourOverTime(TradeMetric):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "time" not in df.columns or "profit" not in df.columns:
            return pd.DataFrame(columns=["time", "hour", "profit"])

        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df["hour"] = df["time"].dt.hour
        df["date"] = df["time"].dt.date

        return (
            df.groupby(["date", "hour"])["profit"]
            .sum()
            .reset_index()
            .rename(columns={"date": "time"})
        )
