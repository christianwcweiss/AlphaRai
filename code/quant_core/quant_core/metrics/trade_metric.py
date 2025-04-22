from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
from dash import dcc
import plotly.graph_objects as go


class TradeMetric(ABC):
    __TITLE__: str
    __SUBTITLE__: Optional[str] = None

    @abstractmethod
    def _run(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def to_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert the metric to a DataFrame."""
        return self._run(df)

    @abstractmethod
    def to_chart(self, df: pd.DataFrame) -> go.Figure:
        pass