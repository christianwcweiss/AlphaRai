import numpy as np
import pytest

from quant_core.features.indicators.nadaraya_watson_envelope import DataFeatureNadarayaWatsonEnvelope
from quant_dev.builder import Builder


class TestDataFeatureNadarayaWatsonEnvelope:
    def test_multiple_columns_with_different_parameters(self) -> None:
        data_frame = Builder().get_random_chart_data_frame()
        bandwidths = Builder().get_random_items([2.0, 5.0, 10.0], 2)
        std_multipliers = Builder().get_random_items([1.0, 2.0, 3.0], 2)

        features = [
            DataFeatureNadarayaWatsonEnvelope(bandwidth=bw, std_multiplier=std)
            for bw, std in zip(bandwidths, std_multipliers)
        ]

        for feature in features:
            data_frame = feature.add_feature(data_frame)

        assert all(column in data_frame.columns for feature in features for column in feature.get_columns())

    @pytest.mark.parametrize(
        "bandwidth,std_multiplier",
        [(5.0, 2.0)],
    )
    def test_output_structure(
        self,
        bandwidth: float,
        std_multiplier: float,
    ) -> None:
        """Checks that output columns exist and values are not NaN at the end."""
        data_frame = Builder().get_random_chart_data_frame()
        feature = DataFeatureNadarayaWatsonEnvelope(
            bandwidth=bandwidth,
            std_multiplier=std_multiplier,
        )

        data_frame = feature.add_feature(data_frame)
        data_frame = feature.normalize_feature(data_frame)

        raw_columns = feature.get_columns()
        normalized_columns = feature.get_feature_columns()

        for col in raw_columns + normalized_columns:
            assert col in data_frame.columns
            assert not np.isnan(data_frame[col].iloc[-1]), f"{col} has NaN at the end"
