import pandas as pd

from quant_core.metrics.trade_metric import TradeMetric


class MaxDrawdownOverTimeRelative(TradeMetric):
    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if data_frame.empty or "profit" not in data_frame.columns:
            return pd.DataFrame(columns=["time", "drawdown_pct"])

        data_frame = data_frame.sort_values("time").copy()
        data_frame["equity"] = data_frame["profit"].cumsum()
        data_frame["peak"] = data_frame["equity"].cummax()

        # Avoid division by zero
        data_frame["drawdown_pct"] = data_frame.apply(
            lambda row: ((row["peak"] - row["equity"]) / row["peak"] * 100) if row["peak"] > 0 else 0.0,
            axis=1,
        )

        return data_frame[["time", "drawdown_pct"]]
