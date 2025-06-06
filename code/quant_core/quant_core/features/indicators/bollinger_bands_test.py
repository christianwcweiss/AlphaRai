from typing import List

import pytest
from quant_core.chart.features.indicators.bollinger_bands import DataFeatureBollingerBands
from quant_dev.builder import Builder


class TestDataFeatureBollingerBands:
    def test_multiple_columns_with_different_parameters(self) -> None:
        data_frame = Builder().get_random_chart_data_frame()
        bb_lengths = Builder().get_random_items(list(range(1, 100)), 5)
        bb_mult_factors = Builder().get_random_items(list(range(1, 100)), 5)
        features = [
            DataFeatureBollingerBands(bb_length=bb_length, bb_mult_factor=bb_mult_factor)
            for bb_length, bb_mult_factor in zip(bb_lengths, bb_mult_factors)
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
                "eurusd_60.csv",
                20,
                2,
                [
                    1.0484,
                    1.0481,
                    1.0478,
                    1.0476,
                    1.0473,
                    1.0471,
                    1.0470,
                    1.0470,
                    1.0470,
                    1.0470,
                    1.0470,
                    1.0470,
                    1.0470,
                    1.0471,
                    1.0472,
                    1.0473,
                    1.0474,
                    1.0475,
                    1.0476,
                    1.0478,
                ],
                [
                    1.0524,
                    1.0518,
                    1.0511,
                    1.0504,
                    1.0495,
                    1.0486,
                    1.0482,
                    1.0481,
                    1.0482,
                    1.0481,
                    1.0481,
                    1.0481,
                    1.0482,
                    1.0481,
                    1.0485,
                    1.0489,
                    1.0494,
                    1.0498,
                    1.0502,
                    1.0504,
                ],
                [
                    1.0443,
                    1.0445,
                    1.0445,
                    1.0447,
                    1.0451,
                    1.0456,
                    1.0458,
                    1.0459,
                    1.0459,
                    1.0459,
                    1.0458,
                    1.0459,
                    1.0459,
                    1.0460,
                    1.0459,
                    1.0457,
                    1.0454,
                    1.0452,
                    1.0451,
                    1.0452,
                ],
                [
                    0.001588,
                    0.001159,
                    0.001628,
                    0.001187,
                    0.000769,
                    -0.000294,
                    -0.000255,
                    -0.000286,
                    -0.000615,
                    -0.000631,
                    0.000561,
                    -0.000006,
                    -0.000254,
                    -0.000157,
                    -0.001643,
                    -0.001976,
                    -0.002463,
                    -0.002586,
                    -0.002104,
                    -0.001863,
                ],
                [
                    0.004644,
                    0.004778,
                    0.003933,
                    0.002882,
                    0.001129,
                    0.000883,
                    0.000787,
                    0.000491,
                    0.000428,
                    0.001650,
                    0.001081,
                    0.000830,
                    0.000838,
                    -0.000399,
                    -0.000457,
                    -0.000570,
                    -0.000369,
                    0.000315,
                    0.000654,
                ],
                [
                    -0.002257,
                    -0.002326,
                    -0.001522,
                    -0.001560,
                    -0.001345,
                    -0.001716,
                    -0.001393,
                    -0.001359,
                    -0.001722,
                    -0.001691,
                    -0.000528,
                    -0.001093,
                    -0.001337,
                    -0.001152,
                    -0.002887,
                    -0.003496,
                    -0.004355,
                    -0.004803,
                    -0.004522,
                    -0.004380,
                ],
            )
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
        """Compare with manually calculated values for Bollinger Bands."""
        data_frame = Builder().get_random_chart_data_frame(file_name=file_name)
        feature = DataFeatureBollingerBands(bb_length=length, bb_mult_factor=mult_factor)
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
            .apply(lambda x: round(x, 6))[-len(mavg_feature_expected_values) :]
            .values.tolist()
            == mavg_feature_expected_values
        )
        assert (
            data_frame[upper_feature_column]
            .apply(lambda x: round(x, 6))[-len(upper_feature_expected_values) :]
            .values.tolist()
            == upper_feature_expected_values
        )
        assert (
            data_frame[lower_feature_column]
            .apply(lambda x: round(x, 6))[-len(lower_feature_expected_values) :]
            .values.tolist()
            == lower_feature_expected_values
        )
