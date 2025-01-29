import abc
from typing import List

import pandas as pd


class DataFeature(abc.ABC):
    @abc.abstractmethod
    def get_columns(self) -> List[str]:
        pass

    @abc.abstractmethod
    def get_feature_columns(self) -> List[str]:
        pass

    @abc.abstractmethod
    def add_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def normalize_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        pass
