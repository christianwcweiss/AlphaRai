import pandas as pd
from quant_core.metrics.trade_metric import TradeMetricOverTime


class RiskRewardRatioOverTime(TradeMetricOverTime):
    def calculate_grouped(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df = df[df["profit"].notna()]
        result = []

        for current_day, window_df in self.get_rolling_windows(df, skip_head=True).items():
            for account, group in window_df.groupby("account_id"):
                wins = group[group["profit"] > 0]
                losses = group[group["profit"] < 0]

                avg_win = wins["profit"].mean() if not wins.empty else 0.0
                avg_loss = abs(losses["profit"].mean()) if not losses.empty else 1e-6  # prevent division by zero

                rr = avg_win / avg_loss
                result.append({"time": current_day, "account_id": account, "risk_reward": round(rr, 2)})

        return pd.DataFrame(result)

    def calculate_ungrouped(self, df: pd.DataFrame) -> pd.DataFrame:
        grouped = self.calculate_grouped(df)
        return grouped.groupby("time")["risk_reward"].mean().reset_index()
