import pandas as pd
from quant_core.metrics.trade_metric import TradeMetricOverTime


class SharpeRatioOverTime(TradeMetricOverTime):
    def calculate_grouped(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df = df[df["profit"].notna()]
        result = []

        for current_day, window_df in self.get_rolling_windows(df, skip_head=True).items():
            for account, group in window_df.groupby("account_id"):
                daily_returns = group.groupby("time")["profit"].sum()

                if len(daily_returns) < 2:
                    sharpe = 0.0
                else:
                    mean_return = daily_returns.mean()
                    std_return = daily_returns.std()
                    sharpe = mean_return / std_return if std_return > 0 else 0.0

                result.append({
                    "time": current_day,
                    "account_id": account,
                    "sharpe": round(sharpe, 2)
                })

        return pd.DataFrame(result)

    def calculate_ungrouped(self, df: pd.DataFrame) -> pd.DataFrame:
        grouped = self.calculate_grouped(df)
        return (
            grouped.groupby("time")["sharpe"]
            .mean()
            .reset_index()
        )
