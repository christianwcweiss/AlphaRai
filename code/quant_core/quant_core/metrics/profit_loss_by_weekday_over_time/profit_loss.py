import pandas as pd
from quant_core.metrics.trade_metric import TradeMetricOverTime


class ProfitByWeekdayOverTime(TradeMetricOverTime):
    def calculate_grouped(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "time" not in df.columns or "profit" not in df.columns:
            return pd.DataFrame(columns=["account_id", "weekday", "avg_profit"])

        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        result = []

        for _, window_df in self.get_rolling_windows(df, skip_head=True).items():
            window_df["weekday"] = window_df["time"].dt.day_name()
            for account, group in window_df.groupby("account_id"):
                weekday_group = group.groupby("weekday")["profit"].mean().reset_index(name="avg_profit")
                weekday_group["account_id"] = account
                result.extend(weekday_group.to_dict(orient="records"))

        return pd.DataFrame(result)

    def calculate_ungrouped(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df["weekday"] = df["time"].dt.day_name()
        return (
            df.groupby("weekday")["profit"]
            .mean()
            .reset_index(name="avg_profit")
        )
