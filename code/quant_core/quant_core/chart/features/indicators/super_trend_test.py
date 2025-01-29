from typing import List

import pytest

from quant_core.chart.features.indicators.super_trend import DataFeatureSuperTrend
from quant_dev.builder import Builder


class TestDataFeatureSuperTrend:
    def test_multiple_columns_with_different_parameters(self) -> None:
        data_frame = Builder().get_random_chart_data_frame()
        factors = Builder().get_random_items([round(Builder.build_random_float()) for _ in range(5)], 5)
        atr_periods = Builder().get_random_items(list(range(1, 100)), 5)

        features = [
            DataFeatureSuperTrend(factor=factor, atr_period=atr_period)
            for factor, atr_period in zip(factors, atr_periods)
        ]

        for feature in features:
            data_frame = feature.add_feature(data_frame)

        assert all(column in data_frame.columns for feature in features for column in feature.get_columns())

    @pytest.mark.parametrize(
        ",".join(
            [
                "file_name",
                "factor",
                "atr_period",
                "supertrend_expected_values",
                "supertrend_direction_expected_values",
                "supertrend_feature_expected_values",
            ]
        ),
        [
            (
                "appl_1440.csv",
                3.0,
                10,
                [
                    238.70,
                    218.33,
                    221.17,
                    221.17,
                    221.17,
                    221.17,
                    221.17,
                    221.17,
                    221.17,
                    221.17,
                    221.17,
                    221.17,
                    221.17,
                    224.77,
                    225.96,
                    227.93,
                    229.81,
                    231.77,
                    231.77,
                    232.45,
                ],
                [-1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [
                    0.0020,
                    -0.0877,
                    -0.0689,
                    -0.0619,
                    -0.0296,
                    -0.0496,
                    -0.0483,
                    -0.0513,
                    -0.0284,
                    -0.0283,
                    -0.0492,
                    -0.0661,
                    -0.0840,
                    -0.0822,
                    -0.0753,
                    -0.0688,
                    -0.0653,
                    -0.0561,
                    -0.0624,
                    -0.0685,
                ],
            ),
            (
                "btcusd_240.csv",
                5,
                14,
                [
                    102715.91,
                    102503.61,
                    101753.63,
                    101561.73,
                    101336.97,
                    101336.97,
                    101336.97,
                    101336.97,
                    101336.97,
                    101336.97,
                    101336.97,
                    101336.97,
                    101336.97,
                    101336.97,
                    101336.97,
                    101336.97,
                    101272.41,
                    101234.24,
                    101234.24,
                    101234.24,
                ],
                [
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                    -1,
                ],
                [
                    0.0578,
                    0.0613,
                    0.0546,
                    0.0575,
                    0.0509,
                    0.0470,
                    0.0410,
                    0.0382,
                    0.0426,
                    0.0401,
                    0.0398,
                    0.0385,
                    0.0306,
                    0.0324,
                    0.0436,
                    0.0655,
                    0.0577,
                    0.0617,
                    0.0530,
                    0.0494,
                ],
            ),
        ],
    )
    def test_correct_calculation(
        self,
        file_name: str,
        factor: float,
        atr_period: int,
        supertrend_expected_values: List[float],
        supertrend_direction_expected_values: List[int],
        supertrend_feature_expected_values: List[float],
    ) -> None:
        """Compare with manually calculated values for SuperTrend."""
        data_frame = Builder().get_random_chart_data_frame(file_name=file_name)
        feature = DataFeatureSuperTrend(factor=factor, atr_period=atr_period)

        supertrend_column, supertrend_direction_column = feature.get_columns()
        supertrend_feature_column = feature.get_feature_columns()[0]

        data_frame = feature.add_feature(data_frame)
        data_frame = feature.normalize_feature(data_frame)

        assert (
            data_frame[supertrend_column]
            .apply(lambda x: round(x, 2))[-len(supertrend_expected_values) :]
            .values.tolist()
            == supertrend_expected_values
        )
        assert (
            data_frame[supertrend_direction_column]
            .apply(lambda x: round(x, 2))[-len(supertrend_direction_expected_values) :]
            .values.tolist()
            == supertrend_direction_expected_values
        )
        assert (
            data_frame[supertrend_feature_column]
            .apply(lambda x: round(x, 4))[-len(supertrend_feature_expected_values) :]
            .values.tolist()
            == supertrend_feature_expected_values
        )
