from typing import List

import numpy as np
import pandas as pd

from quant_core.features.feature import DataFeature
from quant_core.features.indicators.average_true_range import DataFeatureAverageTrueRange
from quant_core.utils.chart_utils import check_df_sorted, check_enough_rows


class DataFeatureSuperTrend(DataFeature):
    """Data Feature for SuperTrend indicator."""

    def __init__(self, factor: float = 3.0, atr_period: int = 14) -> None:
        self._factor = factor
        self._atr_period = atr_period

    def get_columns(self) -> List[str]:
        return [f"super_trend_{self._factor}_{self._atr_period}", f"st_direction_{self._factor}_{self._atr_period}"]

    def add_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:  # pylint: disable=too-many-branches
        st_value_column, st_direction_column = self.get_columns()
        if all(col in data_frame.columns for col in (st_value_column, st_direction_column)):
            return data_frame

        check_df_sorted(data_frame=data_frame)
        check_enough_rows(data_frame=data_frame)

        atr_feature = DataFeatureAverageTrueRange(self._atr_period)
        atr_column = atr_feature.get_columns()[0]
        data_frame = atr_feature.add_feature(data_frame)

        mid = (data_frame["high"] + data_frame["low"]) / 2.0
        basic_upper_band = mid + self._factor * data_frame[atr_column]
        basic_lower_band = mid - self._factor * data_frame[atr_column]

        final_upper_band = np.zeros(len(data_frame))
        final_lower_band = np.zeros(len(data_frame))
        supertrend = np.zeros(len(data_frame))
        direction = np.zeros(len(data_frame))

        final_upper_band[0] = basic_upper_band.iloc[0]
        final_lower_band[0] = basic_lower_band.iloc[0]
        supertrend[0] = np.nan
        direction[0] = 1

        for i in range(1, len(data_frame)):
            if data_frame["close"].iloc[i - 1] <= final_upper_band[i - 1]:
                final_upper_band[i] = min(basic_upper_band.iloc[i], final_upper_band[i - 1])  # type: ignore
            else:
                final_upper_band[i] = basic_upper_band.iloc[i]

            if data_frame["close"].iloc[i - 1] >= final_lower_band[i - 1]:
                final_lower_band[i] = max(basic_lower_band.iloc[i], final_lower_band[i - 1])  # type: ignore
            else:
                final_lower_band[i] = basic_lower_band.iloc[i]

            if supertrend[i - 1] == final_upper_band[i - 1]:
                if data_frame["close"].iloc[i] <= final_upper_band[i]:
                    supertrend[i] = final_upper_band[i]
                    direction[i] = -1
                else:
                    supertrend[i] = final_lower_band[i]
                    direction[i] = 1
            elif supertrend[i - 1] == final_lower_band[i - 1]:
                if data_frame["close"].iloc[i] >= final_lower_band[i]:
                    supertrend[i] = final_lower_band[i]
                    direction[i] = 1
                else:
                    supertrend[i] = final_upper_band[i]
                    direction[i] = -1
            else:
                if data_frame["close"].iloc[i] >= final_lower_band[i]:
                    supertrend[i] = final_lower_band[i]
                    direction[i] = 1
                else:
                    supertrend[i] = final_upper_band[i]
                    direction[i] = -1

        data_frame[st_value_column] = supertrend
        data_frame[st_direction_column] = np.where(direction > 0, 1, -1)

        return data_frame

    def normalize_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        indicator_column_name = self.get_columns()[0]
        normalized_column_name = self.get_feature_columns()[0]

        data_frame[normalized_column_name] = (data_frame[indicator_column_name] - data_frame["close"]) / data_frame[
            "close"
        ]

        return data_frame

    def get_feature_columns(self) -> List[str]:
        return [f"{self.get_columns()[0]}_normalized"]
