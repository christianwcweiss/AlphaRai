import pandas as pd

from quant_core.metrics.trade_metric import TradeMetric

class SortinoRatioOverTime(TradeMetric):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df["time"] = pd.to_datetime(df["time"]).dt.date
        result = []

        for time, group in df.groupby("time"):
            mean = group["profit"].mean()
            downside_std = group[group["profit"] < 0]["profit"].std()

            sortino = mean / downside_std if downside_std > 0 else 0.0
            result.append({"time": time, "sortino": round(sortino, 2)})

        return pd.DataFrame(result)
