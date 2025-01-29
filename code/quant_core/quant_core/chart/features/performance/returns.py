from typing import List

import pandas as pd

from quant_core.chart.feature import DataFeature
from quant_core.enums.trade_direction import TradeDirection
from quant_core.utils.chart_utils import check_df_sorted, check_enough_rows


class DataFeatureReturns(DataFeature):

    def __init__(
        self,
        direction: TradeDirection,
        horizon: int = 1,
    ) -> None:
        self._direction = direction.normalize()
        self._horizon = horizon

    def get_columns(self) -> List[str]:
        return [f"returns_{self._direction.value}_{self._horizon}"]

    def add_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        returns_column = self.get_columns()[0]
        if returns_column in data_frame:
            return data_frame

        check_df_sorted(data_frame=data_frame)
        check_enough_rows(data_frame=data_frame)

        data_frame[returns_column] = data_frame["close"].pct_change(periods=self._horizon)
        if self._direction is TradeDirection.SHORT:
            data_frame[returns_column] *= -1

        return data_frame

    def normalize_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        returns_column = self.get_columns()[0]
        normalized_column = self.get_feature_columns()[0]

        data_frame[normalized_column] = data_frame[returns_column]

        return data_frame

    def get_feature_columns(self) -> List[str]:
        return self.get_columns()
