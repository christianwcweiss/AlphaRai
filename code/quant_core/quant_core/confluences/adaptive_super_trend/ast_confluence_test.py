from typing import Any, Dict

import pandas as pd
import pytest

from quant_core.confluences.adaptive_super_trend.ast_confluence import ConfluenceAdaptiveSuperTrendDirection
from quant_core.confluences.confluence import Confluence
from quant_core.enums.trade_direction import TradeDirection
from quant_core.features.indicators.adaptive_super_trend import DataFeatureAdaptiveSuperTrend


class TestConfluenceAdaptiveSuperTrendDirection:

    @pytest.mark.parametrize(
        "score, min_value, max_value, expected",
        [
            (0.0, 0.8, 1.2, 0.8),
            (0.5, 0.8, 1.2, 1.0),
            (1.0, 0.8, 1.2, 1.2),
        ]

    )
    def test_normalize(
        self, score: float, min_value: float, max_value: float, expected: float
    ) -> None:
        confluence = ConfluenceAdaptiveSuperTrendDirection(config={})

        result = confluence.normalize(score, min_value, max_value)

        assert result == expected