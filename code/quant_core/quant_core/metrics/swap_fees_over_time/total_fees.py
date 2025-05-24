import pandas as pd
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class NetProfitAfterFeesOverTime(TradeMetricOverTime):
    """Calculates the net profit after fees over time."""

    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if (
            data_frame.empty
            or "profit" not in data_frame.columns
            or "commission" not in data_frame.columns
            or "swap" not in data_frame.columns
        ):
            return pd.DataFrame(columns=["time", "net_profit"])

        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"]).dt.date
        data_frame["net"] = data_frame["profit"] - data_frame["commission"] - data_frame["swap"]

        return data_frame.groupby("time")["net"].sum().reset_index().rename(columns={"net": "net_profit"})
