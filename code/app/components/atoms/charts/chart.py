import abc
from typing import Optional, List, Dict, Any

import pandas as pd
import plotly.graph_objects as go


class ChartMargin(abc.ABC):
    def __init__(
        self,
        left: float = 0.0,
        right: float = 0.0,
        top: float = 0.0,
        bottom: float = 0.0,
    ) -> None:
        self._left = left
        self._right = right
        self._top = top
        self._bottom = bottom

    @property
    def margins(self) -> Dict[str, float]:
        """Return the margins as a dictionary."""
        return {
            "l": self._left,
            "r": self._right,
            "t": self._top,
            "b": self._bottom
        }


class ChartStyle(abc.ABC):

    @abc.abstractmethod
    def to_style_dict(self) -> Dict[str, Any]:
        """Convert the chart style to a dictionary for Plotly."""
        pass


class Chart(abc.ABC):
    _chart_style: ChartStyle
    _data_frame: pd.DataFrame

    @abc.abstractmethod
    def plot(self, *args, **kwargs) -> go.Figure:
        """Plot the chart with the given x and y columns."""
        pass
