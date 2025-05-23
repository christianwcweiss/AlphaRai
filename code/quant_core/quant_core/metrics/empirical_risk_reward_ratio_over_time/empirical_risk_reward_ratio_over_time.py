import pandas as pd
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class RiskRewardRatioOverTime(TradeMetricOverTime):
    """Risk-Reward Ratio Over Time."""

    def calculate(
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = True,
        group_by_symbol: bool = True,
        period_window: int = 30,
    ) -> pd.DataFrame:
        groups = self.groups(group_by_account_id=group_by_account_id, group_by_symbol=group_by_symbol)

        data_frame = self._normalize_time(data_frame)

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
