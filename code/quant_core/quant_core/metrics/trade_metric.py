from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
from dash import dcc
import plotly.graph_objects as go


class TradeMetric(ABC):
    @abstractmethod
    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        pass
