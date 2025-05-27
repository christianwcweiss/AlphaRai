from typing import List

import pytest

from quant_core.chart.features.indicators.squeeze_momentum import DataFeatureSqueezeMomentum
from quant_dev.builder import Builder


class TestDataFeatureKeltnerChannel:
    def test_multiple_columns_with_different_parameters(self) -> None:
        data_frame = Builder().get_random_chart_data_frame()
        bb_lengths = Builder().get_random_items(list(range(1, 100)), 2)
        bb_mult_factors = Builder().get_random_items(list(range(1, 100)), 2)
        kc_lengths = Builder().get_random_items(list(range(1, 100)), 2)
        kc_mult_factors = Builder().get_random_items(list(range(1, 100)), 2)
        linreg_windows = Builder().get_random_items(list(range(1, 100)), 2)

        features = [
            DataFeatureSqueezeMomentum(bb_length, bb_mult_factor, kc_length, kc_mult_factor, linreg_window)
            for bb_length, bb_mult_factor, kc_length, kc_mult_factor, linreg_window in zip(
                bb_lengths, bb_mult_factors, kc_lengths, kc_mult_factors, linreg_windows
            )
        ]

        for feature in features:
            data_frame = feature.add_feature(data_frame)

        assert all(column in data_frame.columns for feature in features for column in feature.get_columns())

    @pytest.mark.parametrize(
        ",".join(
            [
                "file_name",
                "bb_length",
                "bb_mult_factor",
                "kc_length",
                "kc_mult_factor",
                "linreg_window",
                "squeeze_on_expected_values",
                "squeeze_off_expected_values",
                "no_squeeze_expected_values",
                "squeeze_values_expected_values",
                "squeeze_values_normalized_expected_values",
            ]
        ),
        [
            (
                "appl_1440.csv",
                20,
                2,
                20,
                2,
                20,
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                ],
                [
                    -16.50,
                    -12.60,
                    -9.35,
                    -6.40,
                    -5.48,
                    -3.68,
                    -1.81,
                    -0.10,
                    0.62,
                    0.97,
                    2.03,
                    3.60,
                    6.23,
                    8.32,
                    10.03,
                    10.89,
                    11.52,
                    11.57,
                    11.31,
                    11.65,
                ],
                [
                    -0.165,
                    -0.126,
                    -0.0935,
                    -0.0640,
                    -0.0548,
                    -0.0368,
                    -0.0181,
                    -0.0010,
                    0.0062,
                    0.0097,
                    0.0203,
                    0.0360,
                    0.0623,
                    0.0832,
                    0.1003,
                    0.1089,
                    0.1152,
                    0.1157,
                    0.1131,
                    0.1165,
                ],
            )
        ],
    )
    def test_correct_calculation(
        self,
        file_name: str,
        bb_length: int,
        bb_mult_factor: int,
        kc_length: int,
        kc_mult_factor: int,
        linreg_window: int,
        squeeze_on_expected_values: List[float],
        squeeze_off_expected_values: List[float],
        no_squeeze_expected_values: List[float],
        squeeze_values_expected_values: List[float],
        squeeze_values_normalized_expected_values: List[float],
    ) -> None:
        """Compare with manually calculated values for Squeeze Momentum."""
        data_frame = Builder().get_random_chart_data_frame(file_name=file_name)
        feature = DataFeatureSqueezeMomentum(
            bb_length=bb_length,
            bb_mult_factor=bb_mult_factor,
            kc_length=kc_length,
            kc_mult_factor=kc_mult_factor,
            linreg_window=linreg_window,
        )
        sqz_on_column, sqz_off_column, no_sqz_column, sqz_value_column = feature.get_columns()
        sqz_value_feature_column = feature.get_feature_columns()[0]

        data_frame = feature.add_feature(data_frame)
        data_frame = feature.normalize_feature(data_frame)

        assert (
            data_frame[sqz_on_column][-len(squeeze_on_expected_values) :].values.tolist() == squeeze_on_expected_values
        )
        assert (
            data_frame[sqz_off_column][-len(squeeze_off_expected_values) :].values.tolist()
            == squeeze_off_expected_values
        )
        assert (
            data_frame[no_sqz_column][-len(no_squeeze_expected_values) :].values.tolist() == no_squeeze_expected_values
        )
        assert (
            data_frame[sqz_value_column]
            .apply(lambda x: round(x, 2))[-len(squeeze_values_expected_values) :]
            .values.tolist()
            == squeeze_values_expected_values
        )
        assert (
            data_frame[sqz_value_feature_column]
            .apply(lambda x: round(x, 4))[-len(squeeze_values_normalized_expected_values) :]
            .values.tolist()
            == squeeze_values_normalized_expected_values
        )
