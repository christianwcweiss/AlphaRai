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
        return {"l": self._left, "r": self._right, "t": self._top, "b": self._bottom}


class ChartLayoutStyle:
    def __init__(
        self,
        title: Optional[str] = None,
        x_axis_title: Optional[str] = None,
        y_axis_title: Optional[str] = None,
        show_legend: bool = False,
        margin: ChartMargin = ChartMargin(),
        x_range: Optional[List[float]] = None,
        y_range: Optional[List[float]] = None,
        show_title: bool = True,
        show_x_title: bool = True,
        show_y_title: bool = True,
        show_x_grid: bool = True,
        show_y_grid: bool = True,
        show_x_axis: bool = True,
        show_y_axis: bool = True,
    ) -> None:
        self.title = title or ""
        self.x_axis_title = x_axis_title or ""
        self.y_axis_title = y_axis_title or ""

        self.show_legend = show_legend
        self.margin = margin
        self.x_range = x_range
        self.y_range = y_range

        self.show_title = show_title
        self.show_x_title = show_x_title
        self.show_y_title = show_y_title
        self.show_x_grid = show_x_grid
        self.show_y_grid = show_y_grid
        self.show_x_axis = show_x_axis
        self.show_y_axis = show_y_axis

    def to_layout_dict(self) -> Dict[str, Any]:
        layout = {
            "title": {
                "text": self.title if self.show_title and self.title else "",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 20, "family": "Arial, sans-serif"},
            },
            "xaxis": {
                "visible": self.show_x_axis,  # 👈 key line to hide the axis
                "title": self.x_axis_title if self.show_x_title and self.x_axis_title else "",
                "range": self.x_range,
                "automargin": True,
                "showgrid": self.show_x_grid,
                "gridcolor": "rgba(200, 200, 200, 0.3)",
            },
            "yaxis": {
                "visible": self.show_y_axis,  # 👈 same for y-axis
                "title": self.y_axis_title if self.show_y_title and self.y_axis_title else "",
                "range": self.y_range,
                "automargin": True,
                "showgrid": self.show_y_grid,
                "gridcolor": "rgba(200, 200, 200, 0.3)",
            },
            "plot_bgcolor": "white",
            "paper_bgcolor": "white",
            "margin": self.margin.margins,
            "legend": {
                "orientation": "h",
                "yanchor": "bottom",
                "y": -0.2,
                "xanchor": "center",
                "x": 0.5,
                "font": {"size": 14},
            },
            "showlegend": self.show_legend,
        }

        return layout


class ChartTraceStyle(abc.ABC):
    @abc.abstractmethod
    def to_style_dict(self) -> Dict[str, Any]:
        """Convert the chart style to a dictionary for Plotly."""
        pass


class Chart(abc.ABC):
    _layout_style: ChartLayoutStyle
    _trace_style: ChartTraceStyle
    _data_frame: pd.DataFrame

    @abc.abstractmethod
    def plot(self, *args, **kwargs) -> go.Figure:
        """Plot the chart with the given x and y columns."""
        pass
