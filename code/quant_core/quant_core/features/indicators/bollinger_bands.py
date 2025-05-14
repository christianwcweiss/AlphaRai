from typing import List

import pandas as pd
from ta.volatility import BollingerBands

from quant_core.features.feature import DataFeature
from quant_core.utils.chart_utils import check_df_sorted, check_enough_rows


class DataFeatureBollingerBands(DataFeature):
    """DataFeature for Bollinger Bands."""

    def __init__(self, bb_length: int = 20, bb_mult_factor: int = 2) -> None:
        self._bb_length = bb_length
        self._bb_mult_factor = bb_mult_factor

    def get_columns(self) -> List[str]:
        return [
            f"bb_mavg_{self._bb_length}_{self._bb_mult_factor}",
            f"bb_upper_{self._bb_length}_{self._bb_mult_factor}",
            f"bb_lower_{self._bb_length}_{self._bb_mult_factor}",
        ]

    def add_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        bb_mavg_column, bb_upper_column, bb_lower_column = self.get_columns()
        if all(col in data_frame.columns for col in (bb_mavg_column, bb_upper_column, bb_lower_column)):
            return data_frame

        check_df_sorted(data_frame=data_frame)
        check_enough_rows(data_frame=data_frame)

        bb = BollingerBands(
            close=data_frame["close"], window=self._bb_length, window_dev=self._bb_mult_factor, fillna=False
        )
        data_frame[bb_mavg_column] = bb.bollinger_mavg()
        data_frame[bb_upper_column] = bb.bollinger_hband()
        data_frame[bb_lower_column] = bb.bollinger_lband()

        return data_frame

    def normalize_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        bb_mavg, bb_upper, bb_lower = self.get_columns()
        bb_mavg_normalized, bb_upper_normalized, bb_lower_normalized = self.get_feature_columns()

        data_frame[bb_mavg_normalized] = (data_frame[bb_mavg] - data_frame["close"]) / data_frame["close"]
        data_frame[bb_upper_normalized] = (data_frame[bb_upper] - data_frame["close"]) / data_frame["close"]
        data_frame[bb_lower_normalized] = (data_frame[bb_lower] - data_frame["close"]) / data_frame["close"]

        return data_frame

    def get_feature_columns(self) -> List[str]:
        return [column + "_normalized" for column in self.get_columns()]
