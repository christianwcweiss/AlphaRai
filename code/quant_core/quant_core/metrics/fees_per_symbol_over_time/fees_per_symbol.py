import pandas as pd
from quant_core.metrics.trade_metric import TradeMetric

class FeesPerSymbolOverTime(TradeMetric):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "commission" not in df.columns or "swap" not in df.columns or "symbol" not in df.columns:
            return pd.DataFrame(columns=["time", "symbol", "fees"])

        df = df.copy()
        df["time"] = pd.to_datetime(df["time"]).dt.date
        df["fees"] = df["commission"] + df["swap"]

        return (
            df.groupby(["time", "symbol"])["fees"]
            .sum()
            .reset_index()
        )
