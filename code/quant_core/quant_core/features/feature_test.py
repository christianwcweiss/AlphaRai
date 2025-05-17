import time

import pytest
from sklearn.utils import shuffle

from quant_core.features.feature import DataFeature
from quant_core.chart.features.indicators.average_true_range import DataFeatureAverageTrueRange
from quant_core.chart.features.indicators.bollinger_bands import DataFeatureBollingerBands
from quant_core.chart.features.indicators.keltner_channel import DataFeatureKeltnerChannel
from quant_dev.builder import Builder


_FEATURES = [
    DataFeatureAverageTrueRange,
    DataFeatureBollingerBands,
    DataFeatureKeltnerChannel,
]


class TestAllFeatures:
    @pytest.mark.parametrize(
        "shuffle_data,reduce_data",
        [
            [True, False],
            [False, True],
            [True, True],
        ],
    )
    @pytest.mark.parametrize("feature", _FEATURES)
    def test_prerequisites_not_fullfilled(self, shuffle_data: bool, reduce_data: bool, feature: DataFeature) -> None:
        data_frame = Builder().get_random_chart_data_frame()

        if shuffle_data:
            data_frame = shuffle(data_frame)

        if reduce_data:
            data_frame = data_frame.tail(100)

        with pytest.raises(AssertionError):
            feature.add_feature(data_frame)

    @pytest.mark.parametrize("feature", _FEATURES)
    def test_caching_active(self, feature: DataFeature) -> None:
        data_frame = Builder().get_random_chart_data_frame()
        column_list = feature.get_columns()

        start_time = time.perf_counter()
        data_frame = feature.add_feature(data_frame)
        first_time = time.perf_counter() - start_time

        assert all(column in data_frame.columns for column in column_list)

        start_time = time.perf_counter()
        data_frame = feature.add_feature(data_frame)
        second_time = time.perf_counter() - start_time

        assert all(column in data_frame.columns for column in column_list)

        assert first_time > second_time
