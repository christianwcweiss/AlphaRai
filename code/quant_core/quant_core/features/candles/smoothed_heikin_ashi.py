from typing import List

import numpy as np
import pandas as pd

from quant_core.features.feature import DataFeature
from quant_core.features.candles.heikin_ashi import DataFeatureHeikinAshi
from quant_core.utils.chart_utils import check_df_sorted, check_enough_rows


class DataFeatureSmoothedHeikinAshi(DataFeature):
    """Data Feature for the Smoothed Heikin Ashi candles."""

    def __init__(self, smooth_length: int) -> None:
        self._smooth_length = smooth_length

    def get_columns(self) -> List[str]:
        return [
            f"ha_open_smooth_{self._smooth_length}",
            f"ha_close_smooth_{self._smooth_length}",
            f"ha_high_smooth_{self._smooth_length}",
            f"ha_low_smooth_{self._smooth_length}",
        ]

    def add_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        sm_ha_open_column, sm_ha_close_column, sm_ha_high_column, sm_ha_low_column = self.get_columns()
        if all(column in data_frame for column in self.get_columns()):
            return data_frame

        check_df_sorted(data_frame)
        check_enough_rows(data_frame)

        ha_feature = DataFeatureHeikinAshi()
        ha_open, ha_close, ha_high, ha_low = ha_feature.get_columns()
        data_frame = ha_feature.add_feature(data_frame)

        data_frame[sm_ha_open_column] = data_frame[ha_open].ewm(span=self._smooth_length, adjust=False).mean()
        data_frame[sm_ha_close_column] = data_frame[ha_close].ewm(span=self._smooth_length, adjust=False).mean()
        data_frame[sm_ha_high_column] = data_frame[ha_high].ewm(span=self._smooth_length, adjust=False).mean()
        data_frame[sm_ha_low_column] = data_frame[ha_low].ewm(span=self._smooth_length, adjust=False).mean()

        data_frame[sm_ha_open_column][: self._smooth_length] = np.nan
        data_frame[sm_ha_close_column][: self._smooth_length] = np.nan
        data_frame[sm_ha_high_column][: self._smooth_length] = np.nan
        data_frame[sm_ha_low_column][: self._smooth_length] = np.nan

        return data_frame

    def normalize_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        sm_ha_open_column, sm_ha_close_column, sm_ha_high_column, sm_ha_low_column = self.get_columns()
        (
            sm_ha_normalized_open_column,
            sm_ha_normalized_close_column,
            sm_ha_normalized_high_column,
            sm_ha_normalized_low_column,
        ) = self.get_feature_columns()

        data_frame[sm_ha_normalized_open_column] = (data_frame[sm_ha_open_column] - data_frame["open"]) / data_frame[
            "open"
        ]
        data_frame[sm_ha_normalized_close_column] = (data_frame[sm_ha_close_column] - data_frame["close"]) / data_frame[
            "close"
        ]
        data_frame[sm_ha_normalized_high_column] = (data_frame[sm_ha_high_column] - data_frame["high"]) / data_frame[
            "high"
        ]
        data_frame[sm_ha_normalized_low_column] = (data_frame[sm_ha_low_column] - data_frame["low"]) / data_frame["low"]

        return data_frame

    def get_feature_columns(self) -> List[str]:
        return [column + "_normalized" for column in self.get_columns()]
