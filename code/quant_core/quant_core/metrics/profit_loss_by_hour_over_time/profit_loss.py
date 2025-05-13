import pandas as pd
from quant_core.metrics.trade_metric import TradeMetricOverTime


class ProfitByHourOverTime(TradeMetricOverTime):
    """Calculates the profit by hour over time."""

    def calculate_grouped(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if data_frame.empty or "time" not in data_frame.columns or "profit" not in data_frame.columns:
            return pd.DataFrame(columns=["account_id", "hour", "profit"])

        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"])
        data_frame["hour"] = data_frame["time"].dt.hour

        result = data_frame.groupby(["account_id", "hour"])["profit"].sum().reset_index()
        return result

    def calculate_ungrouped(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"])
        data_frame["hour"] = data_frame["time"].dt.hour

        return data_frame.groupby("hour")["profit"].sum().reset_index()
