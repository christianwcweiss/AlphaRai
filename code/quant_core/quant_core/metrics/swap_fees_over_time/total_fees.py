import pandas as pd
from quant_core.metrics.trade_metric import TradeMetric

class NetProfitAfterFeesOverTime(TradeMetric):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "profit" not in df.columns or "commission" not in df.columns or "swap" not in df.columns:
            return pd.DataFrame(columns=["time", "net_profit"])

        df = df.copy()
        df["time"] = pd.to_datetime(df["time"]).dt.date
        df["net"] = df["profit"] - df["commission"] - df["swap"]

        return (
            df.groupby("time")["net"]
            .sum()
            .reset_index()
            .rename(columns={"net": "net_profit"})
        )
