from typing import List

import pytest
from quant_core.chart.features.indicators.keltner_channel import DataFeatureKeltnerChannel
from quant_dev.builder import Builder


class TestDataFeatureKeltnerChannel:
    def test_multiple_columns_with_different_parameters(self) -> None:
        data_frame = Builder().get_random_chart_data_frame()
        factors = Builder().get_random_items([round(Builder.build_random_float()) for _ in range(5)], 5)
        atr_periods = Builder().get_random_items(list(range(1, 100)), 5)
        features = [
            DataFeatureKeltnerChannel(kc_length=factor, kc_mult_factor=atr_period)
            for factor, atr_period in zip(factors, atr_periods)
        ]

        for feature in features:
            data_frame = feature.add_feature(data_frame)

        assert all(column in data_frame.columns for feature in features for column in feature.get_columns())

    @pytest.mark.parametrize(
        ",".join(
            [
                "file_name",
                "length",
                "mult_factor",
                "mavg_expected_values",
                "upper_expected_values",
                "lower_expected_values",
                "mavg_feature_expected_values",
                "upper_feature_expected_values",
                "lower_feature_expected_values",
            ]
        ),
        [
            (
                "appl_1440.csv",
                20,
                2,
                [
                    236.8194,
                    235.9171,
                    235.2367,
                    234.6282,
                    233.8081,
                    233.1929,
                    232.4787,
                    231.9489,
                    231.3241,
                    230.9146,
                    230.8684,
                    230.9103,
                    231.0548,
                    231.671,
                    232.356,
                    233.4829,
                    234.6391,
                    235.7479,
                    236.9256,
                    237.9018,
                ],
                [
                    241.9115,
                    241.0191,
                    240.3802,
                    240.2672,
                    239.3906,
                    238.9854,
                    238.3162,
                    237.745,
                    237.2736,
                    236.6796,
                    236.7398,
                    236.9136,
                    237.1915,
                    237.5257,
                    238.1977,
                    239.2141,
                    240.2838,
                    241.3301,
                    242.5162,
                    243.3339,
                ],
                [
                    231.7273,
                    230.815,
                    230.0932,
                    228.9893,
                    228.2256,
                    227.4004,
                    226.6412,
                    226.1529,
                    225.3746,
                    225.1496,
                    224.9971,
                    224.907,
                    224.918,
                    225.8162,
                    226.5142,
                    227.7517,
                    228.9944,
                    230.1658,
                    231.335,
                    232.4697,
                ],
                [
                    -0.0059,
                    -0.0142,
                    -0.0097,
                    -0.0049,
                    0.0258,
                    0.0020,
                    0.0004,
                    -0.0051,
                    0.0162,
                    0.0145,
                    -0.0075,
                    -0.0250,
                    -0.0431,
                    -0.0540,
                    -0.0492,
                    -0.0461,
                    -0.0456,
                    -0.0399,
                    -0.0415,
                    -0.0466,
                ],
                [
                    0.0155,
                    0.0071,
                    0.0120,
                    0.0190,
                    0.0503,
                    0.0269,
                    0.0255,
                    0.0198,
                    0.0423,
                    0.0399,
                    0.0178,
                    0.0004,
                    -0.0177,
                    -0.0301,
                    -0.0252,
                    -0.0227,
                    -0.0227,
                    -0.0172,
                    -0.0189,
                    -0.0249,
                ],
                [
                    -0.0273,
                    -0.0356,
                    -0.0313,
                    -0.0288,
                    0.0013,
                    -0.0228,
                    -0.0248,
                    -0.0299,
                    -0.0099,
                    -0.0108,
                    -0.0327,
                    -0.0503,
                    -0.0685,
                    -0.0780,
                    -0.0731,
                    -0.0696,
                    -0.0686,
                    -0.0627,
                    -0.0641,
                    -0.0684,
                ],
            ),
        ],
    )
    def test_correct_calculation(
        self,
        file_name: str,
        length: int,
        mult_factor: int,
        mavg_expected_values: List[float],
        upper_expected_values: List[float],
        lower_expected_values: List[float],
        mavg_feature_expected_values: List[float],
        upper_feature_expected_values: List[float],
        lower_feature_expected_values: List[float],
    ) -> None:
        """Compare with manually calculated values for Keltner Channel."""
        data_frame = Builder().get_random_chart_data_frame(file_name=file_name)
        feature = DataFeatureKeltnerChannel(kc_length=length, kc_mult_factor=mult_factor)
        mavg_column, upper_column, lower_column = feature.get_columns()
        mavg_feature_column, upper_feature_column, lower_feature_column = feature.get_feature_columns()

        data_frame = feature.add_feature(data_frame)
        data_frame = feature.normalize_feature(data_frame)

        assert (
            data_frame[mavg_column].apply(lambda x: round(x, 4))[-len(mavg_expected_values) :].values.tolist()
            == mavg_expected_values
        )
        assert (
            data_frame[upper_column].apply(lambda x: round(x, 4))[-len(upper_expected_values) :].values.tolist()
            == upper_expected_values
        )
        assert (
            data_frame[lower_column].apply(lambda x: round(x, 4))[-len(lower_expected_values) :].values.tolist()
            == lower_expected_values
        )
        assert (
            data_frame[mavg_feature_column]
            .apply(lambda x: round(x, 4))[-len(mavg_feature_expected_values) :]
            .values.tolist()
            == mavg_feature_expected_values
        )
        assert (
            data_frame[upper_feature_column]
            .apply(lambda x: round(x, 4))[-len(upper_feature_expected_values) :]
            .values.tolist()
            == upper_feature_expected_values
        )
        assert (
            data_frame[lower_feature_column]
            .apply(lambda x: round(x, 4))[-len(lower_feature_expected_values) :]
            .values.tolist()
            == lower_feature_expected_values
        )
