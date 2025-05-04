import pandas as pd
from quant_core.metrics.trade_metric import TradeMetric

class ProfitByWeekdayOverTime(TradeMetric):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "time" not in df.columns or "profit" not in df.columns:
            return pd.DataFrame(columns=["time", "weekday", "avg_profit"])

        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df["weekday"] = df["time"].dt.day_name()
        df["date"] = df["time"].dt.date

        return (
            df.groupby(["date", "weekday"])["profit"]
            .mean()
            .reset_index()
            .rename(columns={"date": "time", "profit": "avg_profit"})
        )
