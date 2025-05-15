import pandas as pd
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class SharpeRatioOverTime(TradeMetricOverTime):
    """Calculates the Sharpe ratio over time."""

    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"])
        data_frame = data_frame[data_frame["profit"].notna()]
        result = []

        for current_day, window_df in self.get_rolling_windows(data_frame, skip_head=True).items():
            for account, group in window_df.groupby("account_id"):
                daily_returns = group.groupby("time")["profit"].sum()

                if len(daily_returns) < 2:
                    sharpe = 0.0
                else:
                    mean_return = daily_returns.mean()
                    std_return = daily_returns.std()
                    sharpe = mean_return / std_return if std_return > 0 else 0.0

                result.append({"time": current_day, "account_id": account, "sharpe": round(sharpe, 2)})

        return pd.DataFrame(result)
