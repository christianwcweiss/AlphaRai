import pandas as pd
from quant_core.metrics.trade_metric import TradeMetric

class TradesPerDay(TradeMetric):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "time" not in df.columns:
            return pd.DataFrame(columns=["time", "trade_count"])

        df = df.copy()
        df["time"] = pd.to_datetime(df["time"]).dt.date
        return df.groupby("time").size().reset_index(name="trade_count")
