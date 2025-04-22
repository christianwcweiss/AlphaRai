import abc
from typing import Optional, List

import pandas as pd
import plotly.graph_objects as go

class Chart(abc.ABC):
    __BACKGROUND__ = "lightgray"  # Fixed background color for all charts

    def __init__(self, title: str, subtitle: str = "", show_legend: bool = True,
                 show_x_title: bool = True, show_y_title: bool = True) -> None:
        if not title:
            raise ValueError("Title is mandatory.")
        self.title = title
        self.subtitle = subtitle
        self.show_legend = show_legend
        self.show_x_title = show_x_title
        self.show_y_title = show_y_title

    @abc.abstractmethod
    def plot(self, data_frame: pd.DataFrame, x_col: str, y_col: List[str], groupby: Optional[str] = None) -> go.Figure:
        """Plot the chart with the given x and y columns."""
        pass