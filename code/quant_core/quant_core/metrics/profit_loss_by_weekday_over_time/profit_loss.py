import pandas as pd
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class ProfitByWeekdayOverTime(TradeMetricOverTime):
    """Calculates the profit by weekday over time."""

    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if data_frame.empty or "time" not in data_frame.columns or "profit" not in data_frame.columns:
            return pd.DataFrame(columns=["account_id", "weekday", "avg_profit"])

        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"])
        result = []

        for _, window_df in self.get_rolling_windows(data_frame, skip_head=True).items():
            window_df["weekday"] = window_df["time"].dt.day_name()
            for account, group in window_df.groupby("account_id"):
                weekday_group = group.groupby("weekday")["profit"].mean().reset_index(name="avg_profit")
                weekday_group["account_id"] = account
                result.extend(weekday_group.to_dict(orient="records"))

        return pd.DataFrame(result)
