import pandas as pd
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class FeesPerSymbolOverTime(TradeMetricOverTime):
    """Fees per symbol over time."""

    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if (
            data_frame.empty
            or "commission" not in data_frame.columns
            or "swap" not in data_frame.columns
            or "symbol" not in data_frame.columns
        ):
            return pd.DataFrame(columns=["time", "symbol", "fees"])

        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"]).dt.date
        data_frame["fees"] = data_frame["commission"] + data_frame["swap"]

        return data_frame.groupby(["time", "symbol"])["fees"].sum().reset_index()
