import pandas as pd
from quant_core.metrics.trade_metric import TradeMetricOverTime


class ProfitByHourOverTime(TradeMetricOverTime):
    def calculate_grouped(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "time" not in df.columns or "profit" not in df.columns:
            return pd.DataFrame(columns=["account_id", "hour", "profit"])

        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df["hour"] = df["time"].dt.hour

        result = df.groupby(["account_id", "hour"])["profit"].sum().reset_index()
        return result

    def calculate_ungrouped(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df["hour"] = df["time"].dt.hour

        return df.groupby("hour")["profit"].sum().reset_index()
