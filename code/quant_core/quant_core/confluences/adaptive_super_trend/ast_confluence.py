from typing import Any, Dict

import pandas as pd
from quant_core.confluences.confluence import Confluence
from quant_core.enums.trade_direction import TradeDirection
from quant_core.features.indicators.adaptive_super_trend import DataFeatureAdaptiveSuperTrend


class ConfluenceAdaptiveSuperTrendDirection(Confluence):
    """Confluence that checks if the Adaptive SuperTrend indicator aligns with the trade direction."""

    __NAME__ = "Adaptive SuperTrend Direction"
    __DESCRIPTION__ = "Scores 1.0 if SuperTrend aligns with trade direction, 0.0 if opposite, 0.5 if unknown."

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._atr_period = config.get("atr_period", 10)
        self._min_factor = config.get("min_factor", 1.0)
        self._max_factor = config.get("max_factor", 5.0)
        self._step = config.get("step", 0.5)
        self._perf_alpha = config.get("perf_alpha", 10.0)
        self._from_cluster = config.get("from_cluster", "Best")

    def check(self, data_frame: pd.DataFrame, direction: TradeDirection) -> float:
        ast = DataFeatureAdaptiveSuperTrend(
            atr_period=self._atr_period,
            min_factor=self._min_factor,
            max_factor=self._max_factor,
            step=self._step,
            perf_alpha=self._perf_alpha,
            from_cluster=self._from_cluster,
        )

        data_frame = ast.add_feature(data_frame)
        direction_column = ast.get_columns()[1]

        if direction_column not in data_frame.columns or data_frame.empty:
            return 0.5

        trend = data_frame[direction_column].iloc[-1]

        if trend not in (0, 1):
            return 0.5

        if direction.normalize() is TradeDirection.LONG.normalize():
            return 1.0 if trend == 1 else 0.0
        if direction.normalize() is TradeDirection.SHORT.normalize():
            return 1.0 if trend == 0 else 0.0

        return 0.5
