import pandas as pd
from quant_core.metrics.trade_metric import TradeMetricOverTime


class TradesPerDayOverTime(TradeMetricOverTime):
    def calculate_grouped(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "time" not in df.columns:
            return pd.DataFrame(columns=["time", "account_id", "trade_count"])

        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        result = []

        for current_day, window_df in self.get_rolling_windows(df, skip_head=True).items():
            for account, group in window_df.groupby("account_id"):
                trade_count = len(group)
                result.append({"time": current_day, "account_id": account, "trade_count": trade_count})

        return pd.DataFrame(result)

    def calculate_ungrouped(self, df: pd.DataFrame) -> pd.DataFrame:
        grouped = self.calculate_grouped(df)
        return grouped.groupby("time")["trade_count"].sum().reset_index()
