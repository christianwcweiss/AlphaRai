import pandas as pd
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class RiskRewardRatioOverTime(TradeMetricOverTime):
    """Risk-Reward Ratio Over Time."""

    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"])
        data_frame = data_frame[data_frame["profit"].notna()]
        result = []

        for current_day, window_df in self.get_rolling_windows(data_frame, skip_head=True).items():
            for account, group in window_df.groupby("account_id"):
                wins = group[group["profit"] > 0]
                losses = group[group["profit"] < 0]

                avg_win = wins["profit"].mean() if not wins.empty else 0.0
                avg_loss = abs(losses["profit"].mean()) if not losses.empty else 1e-6  # prevent division by zero

                rr = avg_win / avg_loss
                result.append({"time": current_day, "account_id": account, "risk_reward": round(rr, 2)})

        return pd.DataFrame(result)
