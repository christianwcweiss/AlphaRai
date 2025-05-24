import pandas as pd
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class TradesPerDayOverTime(TradeMetricOverTime):
    """Trades per day over time metric."""

    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if data_frame.empty or "time" not in data_frame.columns:
            return pd.DataFrame(columns=["time", "account_id", "trade_count"])

        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"])
        result = []

        for current_day, window_df in self.get_rolling_windows(data_frame, skip_head=True).items():
            for account, group in window_df.groupby("account_id"):
                trade_count = len(group)
                result.append({"time": current_day, "account_id": account, "trade_count": trade_count})

        return pd.DataFrame(result)
