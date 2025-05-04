import pandas as pd

from quant_core.metrics.trade_metric import TradeMetric

class KellyCriterionOverTime(TradeMetric):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df["time"] = pd.to_datetime(df["time"]).dt.date
        result = []

        for time, group in df.groupby("time"):
            wins = group[group["profit"] > 0]
            losses = group[group["profit"] < 0]

            win_rate = len(wins) / len(group) if len(group) > 0 else 0.0
            loss_rate = 1 - win_rate
            avg_win = wins["profit"].mean() if not wins.empty else 0.0
            avg_loss = abs(losses["profit"].mean()) if not losses.empty else 1e-6

            rr_ratio = avg_win / avg_loss if avg_loss > 0 else 0.0
            kelly = win_rate - (loss_rate / rr_ratio) if rr_ratio > 0 else 0.0

            result.append({"time": time, "kelly_pct": round(kelly * 100, 2)})

        return pd.DataFrame(result)