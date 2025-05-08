import pandas as pd

from quant_core.metrics.trade_metric import TradeMetricOverTime


class MostTradedSymbols(TradeMetricOverTime):
    def __init__(self, top_n: int = 5):
        self.top_n = top_n

    def calculate_grouped(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if data_frame.empty or "symbol" not in data_frame.columns:
            return pd.DataFrame(columns=["symbol", "trade_count"])

        counts = data_frame["symbol"].value_counts().nlargest(self.top_n).reset_index()
        counts.columns = ["symbol", "trade_count"]
        return counts
