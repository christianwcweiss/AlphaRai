from typing import List

import pytest

from quant_core.chart.features.candles.smoothed_heikin_ashi import DataFeatureSmoothedHeikinAshi
from quant_dev.builder import Builder


class TestDataFeatureSmoothedHeikinAshi:
    def test_multiple_columns_with_different_parameters(self) -> None:
        data_frame = Builder().get_random_chart_data_frame()
        smoothed_ha_lengths = [Builder().build_random_int(1, 100) for _ in range(3)]
        features = [DataFeatureSmoothedHeikinAshi(ha_length) for ha_length in smoothed_ha_lengths]

        for feature in features:
            data_frame = feature.add_feature(data_frame)

        assert all(column in data_frame.columns for feature in features for column in feature.get_columns())

    @pytest.mark.parametrize(
        ",".join(
            [
                "file_name",
                "length",
                "open_expected_values",
                "close_expected_values",
                "high_expected_values",
                "low_expected_values",
                "normalized_open_expected_values",
                "normalized_close_expected_values",
                "normalized_high_expected_values",
                "normalized_low_expected_values",
            ]
        ),
        [
            (
                "appl_1440.csv",
                10,
                [
                    229.2458,
                    230.2078,
                    231.3904,
                    232.6197,
                    234.2136,
                    233.2505,
                    232.6471,
                    232.2288,
                    232.2212,
                    231.8304,
                    231.2352,
                    231.0772,
                    231.6063,
                    232.9854,
                    234.8157,
                    236.5187,
                    238.0055,
                    239.3331,
                    240.4918,
                    241.4953,
                ],
                [
                    230.297,
                    231.4833,
                    232.7708,
                    234.2369,
                    233.2536,
                    232.6441,
                    232.2368,
                    232.2186,
                    231.8769,
                    231.3014,
                    231.2501,
                    231.7277,
                    233.0624,
                    234.8864,
                    236.5138,
                    237.9883,
                    239.3366,
                    240.6065,
                    241.6451,
                    242.8136,
                ],
                [
                    234.0881,
                    235.1333,
                    236.1558,
                    238.1524,
                    238.7404,
                    237.716,
                    236.7925,
                    236.2424,
                    235.8269,
                    234.8687,
                    234.9319,
                    235.2908,
                    236.5699,
                    238.1585,
                    239.4309,
                    240.6155,
                    241.7283,
                    242.9897,
                    244.0474,
                    245.1164,
                ],
                [
                    226.519,
                    227.8841,
                    229.4892,
                    230.2051,
                    229.3853,
                    228.8854,
                    228.7764,
                    229.0619,
                    228.7337,
                    228.4507,
                    228.3918,
                    228.7509,
                    229.7029,
                    231.4281,
                    233.3186,
                    235.1072,
                    236.7725,
                    238.3058,
                    239.4224,
                    240.4194,
                ],
                [
                    -0.0069,
                    -0.0166,
                    -0.0309,
                    -0.0582,
                    0.0187,
                    0.0269,
                    0.0191,
                    0.0042,
                    -0.0012,
                    0.0101,
                    0.0136,
                    -0.0003,
                    -0.0224,
                    -0.034,
                    -0.0376,
                    -0.0331,
                    -0.0276,
                    -0.0265,
                    -0.0177,
                    -0.0259,
                ],
                [
                    -0.0333,
                    -0.0328,
                    -0.0201,
                    -0.0065,
                    0.0234,
                    -0.0003,
                    -0.0007,
                    -0.0039,
                    0.0186,
                    0.0162,
                    -0.0058,
                    -0.0215,
                    -0.0348,
                    -0.0409,
                    -0.0321,
                    -0.0277,
                    -0.0265,
                    -0.0202,
                    -0.0224,
                    -0.0269,
                ],
                [
                    -0.0253,
                    -0.0196,
                    -0.0191,
                    -0.0364,
                    0.03,
                    0.0198,
                    0.0179,
                    0.0106,
                    0.008,
                    0.0187,
                    -0.0012,
                    -0.0068,
                    -0.0238,
                    -0.0291,
                    -0.0234,
                    -0.0217,
                    -0.0203,
                    -0.0228,
                    -0.0191,
                    -0.0192,
                ],
                [
                    -0.0187,
                    -0.0262,
                    -0.0325,
                    -0.0138,
                    0.0163,
                    0.0099,
                    0.0021,
                    -0.0058,
                    0.0065,
                    0.0056,
                    0.0012,
                    -0.0081,
                    -0.0249,
                    -0.0396,
                    -0.0352,
                    -0.0331,
                    -0.0307,
                    -0.0281,
                    -0.0206,
                    -0.0183,
                ],
            ),
        ],
    )
    def test_correct_calculation(
        self,
        file_name: str,
        length: int,
        open_expected_values: List[float],
        close_expected_values: List[float],
        high_expected_values: List[float],
        low_expected_values: List[float],
        normalized_open_expected_values: List[float],
        normalized_close_expected_values: List[float],
        normalized_high_expected_values: List[float],
        normalized_low_expected_values: List[float],
    ) -> None:
        """Compare with manually calculated values for Keltner Channel."""
        data_frame = Builder().get_random_chart_data_frame(file_name=file_name)
        feature = DataFeatureSmoothedHeikinAshi(length)
        ha_open_column, ha_close_column, ha_high_column, ha_low_column = feature.get_columns()
        ha_normalized_open_column, ha_normalized_close_column, ha_normalized_high_column, ha_normalized_low_column = (
            feature.get_feature_columns()
        )

        data_frame = feature.add_feature(data_frame)
        data_frame = feature.normalize_feature(data_frame)

        breakpoint()

        assert (
            data_frame[ha_open_column].apply(lambda x: round(x, 4))[-len(open_expected_values) :].values.tolist()
            == open_expected_values
        )
        assert (
            data_frame[ha_close_column].apply(lambda x: round(x, 4))[-len(close_expected_values) :].values.tolist()
            == close_expected_values
        )
        assert (
            data_frame[ha_high_column].apply(lambda x: round(x, 4))[-len(high_expected_values) :].values.tolist()
            == high_expected_values
        )
        assert (
            data_frame[ha_low_column].apply(lambda x: round(x, 4))[-len(low_expected_values) :].values.tolist()
            == low_expected_values
        )
        assert (
            data_frame[ha_normalized_open_column]
            .apply(lambda x: round(x, 4))[-len(normalized_open_expected_values) :]
            .values.tolist()
            == normalized_open_expected_values
        )
        assert (
            data_frame[ha_normalized_close_column]
            .apply(lambda x: round(x, 4))[-len(normalized_close_expected_values) :]
            .values.tolist()
            == normalized_close_expected_values
        )
        assert (
            data_frame[ha_normalized_high_column]
            .apply(lambda x: round(x, 4))[-len(normalized_high_expected_values) :]
            .values.tolist()
            == normalized_high_expected_values
        )
        assert (
            data_frame[ha_normalized_low_column]
            .apply(lambda x: round(x, 4))[-len(normalized_low_expected_values) :]
            .values.tolist()
            == normalized_low_expected_values
        )
