import pandas as pd

from quant_core.metrics.trade_metric import TradeMetricOverTime


class ExpectancyOverTimeAbsolute(TradeMetricOverTime):

    def __init__(self, rolling_window_days: int = 30) -> None:
        super().__init__(rolling_window_days)

    def calculate_grouped(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df = df[df["profit"].notna()]
        result = []

        for (current_day, window_df) in self.get_rolling_windows(df, skip_head=True).items():
            for account, group in window_df.groupby("account_id"):
                wins = group[group["profit"] > 0]
                losses = group[group["profit"] < 0]

                win_rate = len(wins) / len(group) if len(group) > 0 else 0.0
                avg_win = wins["profit"].mean() if not wins.empty else 0.0
                avg_loss = abs(losses["profit"].mean()) if not losses.empty else 0.0

                expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
                result.append({
                    "time": current_day,
                    "account_id": account,
                    "expectancy": round(expectancy, 2)
                })

        return pd.DataFrame(result)

    def calculate_ungrouped(self, df: pd.DataFrame) -> pd.DataFrame:
        grouped = self.calculate_grouped(df)
        return (
            grouped.groupby("time")["expectancy"]
            .sum()
            .reset_index()
        )