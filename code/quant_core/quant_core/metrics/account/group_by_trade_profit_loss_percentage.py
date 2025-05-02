import pandas as pd

from quant_core.metrics.trade_metric import TradeMetric


class GroupByTradeProfitLossPercentage(TradeMetric):
    def __init__(self, days: int = 90):
        self.days = days

    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("GroupByTradeProfitLossPercentage is not implemented yet.")
