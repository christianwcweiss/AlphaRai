from typing import List

import pytest

from quant_core.chart.features.indicators.adaptive_super_trend import DataFeatureAdaptiveSuperTrend
from quant_dev.builder import Builder


class TestDataFeatureAdaptiveSuperTrend:
    def test_multiple_columns_with_different_parameters(self) -> None:
        file_name = "appl_1440.csv"
        data_frame = Builder().get_random_chart_data_frame(file_name=file_name)
        atr_periods = Builder().get_random_items(list(range(10, 12)), 2)
        factors = [round(Builder.build_random_float(1.0, 1.1)) for _ in range(2)]
        steps = [round(Builder.build_random_float(0.5, 0.6), 3) for _ in range(2)]
        perf_alphas = [round(Builder.build_random_float(10, 10.1), 3) for _ in range(2)]
        from_clusters = Builder().get_random_items(["Best", "Average", "Worst"], 2)

        features = [
            DataFeatureAdaptiveSuperTrend(
                atr_period=atr_period,
                min_factor=factor,
                max_factor=factor + 4,
                step=step,
                perf_alpha=perf_alpha,
                from_cluster=from_cluster,
                max_iter=1000,
                max_data=10000,
            )
            for atr_period, factor, step, perf_alpha, from_cluster in zip(
                atr_periods, factors, steps, perf_alphas, from_clusters
            )
        ]

        for feature in features:
            data_frame = feature.add_feature(data_frame)

        assert all(column in data_frame.columns for feature in features for column in feature.get_columns())

    @pytest.mark.parametrize(
        ",".join(
            [
                "file_name",
                "adaptive_supertrend_expected_values",
                "adaptive_supertrend_direction_expected_values",
                "adaptive_supertrend_feature_expected_values",
            ]
        ),
        [
            (
                "appl_1440.csv",
                [
                    242.83,
                    242.83,
                    242.83,
                    242.83,
                    241.45,
                    234.12,
                    233.79,
                    233.79,
                    233.79,
                    233.79,
                    222.24,
                    223.76,
                    226.36,
                    226.36,
                    226.36,
                    226.36,
                    226.36,
                    226.36,
                    226.36,
                    226.36,
                    226.36,
                    226.36,
                    226.36,
                    230.12,
                    231.07,
                    232.78,
                    234.38,
                    236.19,
                    236.19,
                    236.82,
                ],
                [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
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
                    -0.036,
                    -0.041,
                    -0.021,
                    -0.064,
                    -0.051,
                    -0.052,
                    -0.045,
                    -0.046,
                    -0.049,
                    -0.018,
                    0.067,
                    0.065,
                    0.047,
                    0.040,
                    0.007,
                    0.027,
                    0.026,
                    0.029,
                    0.006,
                    0.005,
                    0.027,
                    0.044,
                    0.063,
                    0.060,
                    0.054,
                    0.049,
                    0.047,
                    0.038,
                    0.044,
                    0.051,
                ],
            )
        ],
    )
    def test_correct_calculation(
        self,
        file_name: str,
        adaptive_supertrend_expected_values: List[float],
        adaptive_supertrend_direction_expected_values: List[int],
        adaptive_supertrend_feature_expected_values: List[float],
    ) -> None:
        """Compare with manually calculated values for SuperTrend."""
        data_frame = Builder().get_random_chart_data_frame(file_name=file_name)
        feature = DataFeatureAdaptiveSuperTrend()

        (
            adapt_st_trend_column,
            adapt_st_direction_column,
            atr_cluster_column,
            lv_new_column,
            mv_new_column,
            hv_new_column,
        ) = feature.get_columns()
        adapt_st_feature_column = feature.get_feature_columns()[0]

        data_frame = feature.add_feature(data_frame)
        data_frame = feature.normalize_feature(data_frame)

        assert (
            data_frame[adapt_st_trend_column]
            .apply(lambda x: round(x, 2))[-len(adaptive_supertrend_expected_values) :]
            .values.tolist()
            == adaptive_supertrend_expected_values
        )
        assert (
            data_frame[adapt_st_direction_column]
            .apply(lambda x: round(x, 2))[-len(adaptive_supertrend_direction_expected_values) :]
            .values.tolist()
            == adaptive_supertrend_direction_expected_values
        )
        assert (
            data_frame[adapt_st_feature_column]
            .apply(lambda x: round(x, 3))[-len(adaptive_supertrend_feature_expected_values) :]
            .values.tolist()
            == adaptive_supertrend_feature_expected_values
        )
