import pandas as pd

from quant_core.metrics.trade_metric import TradeMetric


class RiskRewardRatioOverTime(TradeMetric):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df["time"] = pd.to_datetime(df["time"]).dt.date
        result = []

        for time, group in df.groupby("time"):
            wins = group[group["profit"] > 0]
            losses = group[group["profit"] < 0]

            avg_win = wins["profit"].mean() if not wins.empty else 0.0
            avg_loss = abs(losses["profit"].mean()) if not losses.empty else 1e-6
            rr = avg_win / avg_loss

            result.append({"time": time, "risk_reward": round(rr, 2)})

        return pd.DataFrame(result)
