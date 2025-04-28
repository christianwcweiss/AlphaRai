from abc import ABC, abstractmethod

import pandas as pd


class TradeMetric(ABC):
    @abstractmethod
    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        pass
