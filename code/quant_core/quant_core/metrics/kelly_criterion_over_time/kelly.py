import pandas as pd

from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class KellyCriterionPerAccountOverTime(TradeMetricOverTime):  # pylint: disable=too-few-public-methods
    """Calculate Kelly Criterion per account."""

    def calculate(
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = True,
        group_by_symbol: bool = False,
        rolling_window: int = 30,
    ) -> pd.DataFrame:
        """Calculate Kelly Criterion per account."""
        raise NotImplementedError("Kelly Criterion calculation is not implemented yet.")
