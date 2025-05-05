import pandas as pd
from quant_core.metrics.trade_metric import TradeMetricOverTime

class FeesAsPctOfProfitOverTime(TradeMetricOverTime):
    def calculate_grouped(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "profit" not in df.columns or "commission" not in df.columns or "swap" not in df.columns:
            return pd.DataFrame(columns=["time", "fees_pct"])

        df = df.copy()
        df["time"] = pd.to_datetime(df["time"]).dt.date
        df["fees"] = df["commission"] + df["swap"]

        grouped = df.groupby("time").agg(
            total_fees=("fees", "sum"),
            total_profit=("profit", "sum"),
        ).reset_index()

        grouped["fees_pct"] = grouped.apply(
            lambda row: (row["total_fees"] / row["total_profit"] * 100) if row["total_profit"] != 0 else 0.0,
            axis=1,
        )

        return grouped[["time", "fees_pct"]]
