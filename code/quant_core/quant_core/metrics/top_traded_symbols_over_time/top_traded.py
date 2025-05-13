import pandas as pd

from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class MostTradedSymbols(TradeMetricOverTime):
    """Most Traded Symbols Over Time"""

    def __init__(self, top_n: int = 5) -> None:
        super().__init__()
        self.top_n = top_n

    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if data_frame.empty or "symbol" not in data_frame.columns:
            return pd.DataFrame(columns=["symbol", "trade_count"])

        counts = data_frame["symbol"].value_counts().nlargest(self.top_n).reset_index()
        counts.columns = ["symbol", "trade_count"]
        return counts
