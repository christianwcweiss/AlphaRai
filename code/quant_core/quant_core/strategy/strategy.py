import abc

import pandas as pd

from quant_core.chart.feature import DataFeature
from quant_core.enums.label import PredictionLabel


class Strategy(abc.ABC):
    __TYPE__: str
    __ID__: str
    __FEATURES__: list[DataFeature] = []

    def has_features(self) -> bool:
        return len(self.__FEATURES__) > 0

    def apply_features(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        for feature in self.__FEATURES__:
            data_frame = feature.add_feature(data_frame)
            data_frame = feature.normalize_feature(data_frame)

        return data_frame

    def get_feature_columns(self) -> list[str]:
        feature_columns = []
        for feature in self.__FEATURES__:
            feature_columns.extend(feature.get_feature_columns())

        return feature_columns

    @abc.abstractmethod
    def prepare(
        self,
        data_frame: pd.DataFrame,
    ) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def run(
        self,
        data_frame: pd.DataFrame,
    ) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def get_prediction(
        self,
        data_frame: pd.DataFrame,
    ) -> PredictionLabel:
        pass
