import abc
from typing import List

import pandas as pd


class DataFeature(abc.ABC):
    """Abstract base class for data features."""

    @abc.abstractmethod
    def get_columns(self) -> List[str]:
        """Return the columns for the feature."""

    @abc.abstractmethod
    def get_feature_columns(self) -> List[str]:
        """Return the columns for the normalized feature."""

    @abc.abstractmethod
    def add_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        """Add the feature to the DataFrame."""

    @abc.abstractmethod
    def normalize_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        """Normalize the feature values in the DataFrame."""
