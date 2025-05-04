import pandas as pd

from quant_core.metrics.trade_metric import TradeMetric


class SharpeRatioOverTime(TradeMetric):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df["time"] = pd.to_datetime(df["time"]).dt.date
        result = []

        for time, group in df.groupby("time"):
            mean = group["profit"].mean()
            std = group["profit"].std()

            sharpe = mean / std if std > 0 else 0.0
            result.append({"time": time, "sharpe": round(sharpe, 2)})

        return pd.DataFrame(result)
