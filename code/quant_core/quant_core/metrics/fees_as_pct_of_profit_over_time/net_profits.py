import pandas as pd
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class FeesAsPctOfProfitOverTime(TradeMetricOverTime):
    """Fees as percentage of profit over time metric."""

    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if (
            data_frame.empty
            or "profit" not in data_frame.columns
            or "commission" not in data_frame.columns
            or "swap" not in data_frame.columns
        ):
            return pd.DataFrame(columns=["time", "fees_pct"])

        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"]).dt.date
        data_frame["fees"] = data_frame["commission"] + data_frame["swap"]

        grouped = (
            data_frame.groupby("time")
            .agg(
                total_fees=("fees", "sum"),
                total_profit=("profit", "sum"),
            )
            .reset_index()
        )

        grouped["fees_pct"] = grouped.apply(
            lambda row: (row["total_fees"] / row["total_profit"] * 100) if row["total_profit"] != 0 else 0.0,
            axis=1,
        )

        return grouped[["time", "fees_pct"]]
