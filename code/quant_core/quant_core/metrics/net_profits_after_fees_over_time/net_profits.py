import pandas as pd
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class SwapOverTime(TradeMetricOverTime):
    """Calculates the total swap over time."""

    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if data_frame.empty or "swap" not in data_frame.columns or "time" not in data_frame.columns:
            return pd.DataFrame(columns=["time", "swap"])

        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"]).dt.date

        return data_frame.groupby("time")["swap"].sum().reset_index()
