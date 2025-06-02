from typing import List

import numpy as np
import pandas as pd
from quant_core.features.feature import DataFeature
from quant_core.features.indicators.bollinger_bands import DataFeatureBollingerBands
from quant_core.utils.chart_utils import check_df_sorted, check_enough_rows


class DataFeatureSqueezeMomentum(DataFeature):
    """Data Feature for the Squeeze Momentum Indicator."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        bb_length: int = 20,
        bb_mult_factor: int = 2,
        kc_length: int = 20,
        kc_mult_factor: int = 2,
        linreg_window: int = 20,
    ) -> None:
        self._bb_length = bb_length
        self._bb_mult_factor = bb_mult_factor
        self._kc_length = kc_length
        self._kc_mult_factor = kc_mult_factor
        self._linreg_window = linreg_window

    def get_columns(self) -> List[str]:
        suffix = "_".join(
            [
                str(self._linreg_window),
                str(self._bb_length),
                str(self._bb_mult_factor),
                str(self._kc_length),
                str(self._kc_mult_factor),
            ]
        )

        return [
            f"sqz_on_{suffix}",
            f"sqz_off_{suffix}",
            f"no_sqz_{suffix}",
            f"sqz_val_{suffix}",
        ]

    def add_feature(self, data_frame) -> pd.DataFrame:  # pylint: disable=too-many-locals
        sqz_on_column, sqz_off_column, no_sqz_column, squeeze_val_column = self.get_columns()
        if all(col in data_frame.columns for col in (sqz_on_column, sqz_off_column, no_sqz_column, squeeze_val_column)):
            return data_frame

        check_df_sorted(data_frame=data_frame)
        check_enough_rows(data_frame=data_frame)

        # Bollinger
        bb_feature = DataFeatureBollingerBands(self._bb_length, self._bb_mult_factor)
        data_frame = bb_feature.add_feature(data_frame)
        _, bb_upper_column, bb_lower_column = bb_feature.get_columns()

        # Keltner
        kc_feature = DataFeatureBollingerBands(self._kc_length, self._kc_mult_factor)
        data_frame = kc_feature.add_feature(data_frame)
        _, kc_upper_column, kc_lower_column = kc_feature.get_columns()

        # Squeeze
        data_frame[sqz_on_column] = (data_frame[bb_lower_column] > data_frame[kc_lower_column]) & (
            data_frame[bb_upper_column] < data_frame[kc_upper_column]
        )

        data_frame[sqz_off_column] = (data_frame[bb_lower_column] < data_frame[kc_lower_column]) & (
            data_frame[bb_upper_column] > data_frame[kc_upper_column]
        )
        data_frame[no_sqz_column] = ~(data_frame[sqz_on_column] | data_frame[sqz_off_column])

        rolling_high = data_frame["high"].rolling(self._linreg_window).max()
        rolling_low = data_frame["low"].rolling(self._linreg_window).min()
        avg_hl = 0.5 * (rolling_high + rolling_low)
        avg_cl = data_frame["close"].rolling(self._linreg_window).mean()
        baseline = 0.5 * (avg_hl + avg_cl)
        target_series = data_frame["close"] - baseline

        def rolling_linreg(series: pd.Series, window: int):
            results = np.full(len(series), np.nan)
            x_vals = np.arange(window)
            for i in range(window - 1, len(series)):
                y_window = series.iloc[i - window + 1 : i + 1]
                if y_window.isnull().any():
                    continue
                x_mean = x_vals.mean()
                y_mean = y_window.mean()
                num = np.sum((x_vals - x_mean) * (y_window - y_mean))
                den = np.sum((x_vals - x_mean) ** 2)
                slope = num / den if den != 0 else 0
                intercept = y_mean - slope * x_mean
                results[i] = intercept + slope * (window - 1)
            return pd.Series(results, index=series.index)

        data_frame[squeeze_val_column] = rolling_linreg(target_series, self._linreg_window)

        return data_frame

    def normalize_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        squeeze_val_column = self.get_columns()[-1]
        squeeze_val_feature_column = self.get_feature_columns()[-1]

        data_frame[squeeze_val_feature_column] = data_frame[squeeze_val_column] / 100

        return data_frame

    def get_feature_columns(self) -> List[str]:
        return [self.get_columns()[-1] + "_normalized"]
