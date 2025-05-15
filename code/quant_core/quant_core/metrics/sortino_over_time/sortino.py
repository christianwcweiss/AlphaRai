import pandas as pd
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class SortinoRatioOverTime(TradeMetricOverTime):
    """Calculates the Sortino ratio over time."""

    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"])
        data_frame = data_frame[data_frame["profit"].notna()]
        result = []

        for current_day, window_df in self.get_rolling_windows(data_frame, skip_head=True).items():
            for account, group in window_df.groupby("account_id"):
                daily_returns = group.groupby("time")["profit"].sum()

                if len(daily_returns) < 2:
                    sortino = 0.0
                else:
                    mean_return = daily_returns.mean()
                    downside_returns = daily_returns[daily_returns < 0]

                    downside_std = downside_returns.std()
                    sortino = mean_return / downside_std if downside_std > 0 else 0.0

                result.append({"time": current_day, "account_id": account, "sortino": round(sortino, 2)})

        return pd.DataFrame(result)
