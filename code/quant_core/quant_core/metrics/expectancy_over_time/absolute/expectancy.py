import pandas as pd

from quant_core.metrics.trade_metric import TradeMetric


class ExpectancyOverTimeAbsolute(TradeMetric):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"]).dt.date
        result = []

        for time, group in df.groupby("time"):
            wins = group[group["profit"] > 0]
            losses = group[group["profit"] < 0]

            win_rate = len(wins) / len(group) if len(group) > 0 else 0.0
            avg_win = wins["profit"].mean() if not wins.empty else 0.0
            avg_loss = abs(losses["profit"].mean()) if not losses.empty else 0.0

            expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
            result.append({"time": time, "expectancy": round(expectancy, 2)})

        return pd.DataFrame(result)