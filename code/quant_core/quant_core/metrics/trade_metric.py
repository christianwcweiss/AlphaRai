from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
from dash import dcc
import plotly.graph_objects as go


class TradeMetric(ABC):
    __TITLE__: str
    __SUBTITLE__: Optional[str] = None

    def __init__(self) -> None:
        self._result: Optional[pd.DataFrame] = None

    @abstractmethod
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def to_chart(self, df: pd.DataFrame) -> go.Figure:
        pass