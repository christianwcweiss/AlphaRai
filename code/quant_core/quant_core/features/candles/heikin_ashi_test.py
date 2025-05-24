from typing import List

import pytest

from quant_core.chart.features.candles.heikin_ashi import DataFeatureHeikinAshi
from quant_dev.builder import Builder


class TestDataFeatureHeikinAshi:
    @pytest.mark.parametrize(
        ",".join(
            [
                "file_name",
                "ha_open_expected_values",
                "ha_close_expected_values",
                "ha_high_expected_values",
                "ha_low_expected_values",
                "ha_normalized_open_expected_values",
                "ha_normalized_close_expected_values",
                "ha_normalized_high_expected_values",
                "ha_normalized_low_expected_values",
            ]
        ),
        [
            (
                "appl_1440.csv",
                [
                    226.8415,
                    234.5370,
                    236.7120,
                    238.1515,
                    241.3865,
                    228.9165,
                    229.9315,
                    230.3465,
                    232.1870,
                    230.0720,
                    228.5565,
                    230.3665,
                    233.9870,
                    239.1915,
                    243.0520,
                    244.1820,
                    244.6965,
                    245.3070,
                    245.7060,
                    246.0110,
                ],
                [
                    235.0195,
                    236.8220,
                    238.5643,
                    240.8342,
                    228.8288,
                    229.9012,
                    230.4040,
                    232.1368,
                    230.3395,
                    228.7117,
                    231.0190,
                    233.8768,
                    239.0687,
                    243.0945,
                    243.8367,
                    244.6238,
                    245.4040,
                    246.3210,
                    246.3190,
                    248.0715,
                ],
                [
                    240.1570,
                    239.8370,
                    240.7570,
                    247.1370,
                    241.3865,
                    233.1060,
                    232.6370,
                    233.7670,
                    233.9570,
                    230.5570,
                    235.2160,
                    236.9060,
                    242.3260,
                    245.3070,
                    245.1570,
                    245.9460,
                    246.7360,
                    248.6660,
                    248.8070,
                    249.9270,
                ],
                [
                    226.8415,
                    234.0270,
                    236.7120,
                    233.4270,
                    225.6960,
                    226.6360,
                    228.2860,
                    230.3465,
                    227.2570,
                    227.1770,
                    228.1270,
                    230.3665,
                    233.9870,
                    239.1915,
                    241.8260,
                    243.1560,
                    244.2660,
                    245.2060,
                    244.4470,
                    244.9060,
                ],
                [
                    -0.0174,
                    0.0019,
                    -0.0086,
                    -0.0358,
                    0.0499,
                    0.0078,
                    0.0072,
                    -0.0039,
                    -0.0014,
                    0.0025,
                    0.0019,
                    -0.0034,
                    -0.0124,
                    -0.0083,
                    -0.0039,
                    -0.0018,
                    -0.0002,
                    -0.0022,
                    0.0036,
                    -0.0077,
                ],
                [
                    -0.0135,
                    -0.0105,
                    0.0043,
                    0.0214,
                    0.0040,
                    -0.0121,
                    -0.0086,
                    -0.0042,
                    0.0119,
                    0.0049,
                    -0.0068,
                    -0.0125,
                    -0.0099,
                    -0.0074,
                    -0.0022,
                    -0.0006,
                    -0.0018,
                    0.0031,
                    -0.0035,
                    -0.0059,
                ],
                [0.0, 0.0, 0.0, 0.0, 0.0414, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [
                    -0.0174,
                    0.0,
                    -0.002,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    -0.0003,
                    0.0,
                    0.0,
                    0.0,
                    -0.0011,
                    -0.0067,
                    -0.0074,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                ],
            ),
        ],
    )
    def test_correct_calculation(
        self,
        file_name: str,
        ha_open_expected_values: List[float],
        ha_close_expected_values: List[float],
        ha_high_expected_values: List[float],
        ha_low_expected_values: List[float],
        ha_normalized_open_expected_values: List[float],
        ha_normalized_close_expected_values: List[float],
        ha_normalized_high_expected_values: List[float],
        ha_normalized_low_expected_values: List[float],
    ) -> None:
        """Compare with manually calculated values for Heikin Ashi."""
        data_frame = Builder().get_random_chart_data_frame(file_name=file_name)
        feature = DataFeatureHeikinAshi()
        ha_open_column, ha_close_column, ha_high_column, ha_low_column = feature.get_columns()
        ha_normalized_open_column, ha_normalized_close_column, ha_normalized_high_column, ha_normalized_low_column = (
            feature.get_feature_columns()
        )

        data_frame = feature.add_feature(data_frame)
        data_frame = feature.normalize_feature(data_frame)

        assert (
            data_frame[ha_open_column].apply(lambda x: round(x, 4))[-len(ha_open_expected_values) :].values.tolist()
            == ha_open_expected_values
        )
        assert (
            data_frame[ha_close_column].apply(lambda x: round(x, 4))[-len(ha_close_expected_values) :].values.tolist()
            == ha_close_expected_values
        )
        assert (
            data_frame[ha_high_column].apply(lambda x: round(x, 4))[-len(ha_high_expected_values) :].values.tolist()
            == ha_high_expected_values
        )
        assert (
            data_frame[ha_low_column].apply(lambda x: round(x, 4))[-len(ha_low_expected_values) :].values.tolist()
            == ha_low_expected_values
        )
        assert (
            data_frame[ha_normalized_open_column]
            .apply(lambda x: round(x, 4))[-len(ha_normalized_open_expected_values) :]
            .values.tolist()
            == ha_normalized_open_expected_values
        )
        assert (
            data_frame[ha_normalized_close_column]
            .apply(lambda x: round(x, 4))[-len(ha_normalized_close_expected_values) :]
            .values.tolist()
            == ha_normalized_close_expected_values
        )
        assert (
            data_frame[ha_normalized_high_column]
            .apply(lambda x: round(x, 4))[-len(ha_normalized_high_expected_values) :]
            .values.tolist()
            == ha_normalized_high_expected_values
        )
        assert (
            data_frame[ha_normalized_low_column]
            .apply(lambda x: round(x, 4))[-len(ha_normalized_low_expected_values) :]
            .values.tolist()
            == ha_normalized_low_expected_values
        )
