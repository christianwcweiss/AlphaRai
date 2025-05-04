import pandas as pd

from quant_core.metrics.trade_metric import TradeMetric


class ProfitPerSymbolOverTimeAbsolute(TradeMetric):
    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if data_frame.empty or "symbol" not in data_frame.columns or "profit" not in data_frame.columns:
            return pd.DataFrame(columns=["time", "symbol", "profit"])

        df = data_frame.copy()
        df["time"] = pd.to_datetime(df["time"]).dt.date  # Group by date (not timestamp)

        grouped = (
            df.groupby(["time", "symbol"])["profit"]
            .sum()
            .reset_index()
            .sort_values("time")
        )

        return grouped