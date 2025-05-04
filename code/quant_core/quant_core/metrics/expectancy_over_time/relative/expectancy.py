import pandas as pd

from quant_core.metrics.trade_metric import TradeMetric


class ExpectancyOverTimeRelative(TradeMetric):
    def __init__(self, initial_balance: float = 1_000):  # default if not dynamic
        self.initial_balance = initial_balance

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
            relative_expectancy = expectancy / self.initial_balance * 100

            result.append({"time": time, "expectancy_pct": round(relative_expectancy, 2)})

        return pd.DataFrame(result)
