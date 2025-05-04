import pandas as pd

from quant_core.metrics.trade_metric import TradeMetric


class ProfitFactorOverTime(TradeMetric):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df["time"] = pd.to_datetime(df["time"]).dt.date
        result = []

        for time, group in df.groupby("time"):
            total_profit = group[group["profit"] > 0]["profit"].sum()
            total_loss = abs(group[group["profit"] < 0]["profit"].sum())

            pf = total_profit / total_loss if total_loss > 0 else 0.0
            result.append({"time": time, "profit_factor": round(pf, 2)})

        return pd.DataFrame(result)
