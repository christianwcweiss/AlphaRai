from typing import Any, Dict, Optional

import pandas as pd
import plotly.graph_objects as go
from components.charts.chart import Chart, ChartLayoutStyle, ChartTraceStyle
from constants.colors import CHART_PALETTE


class BarChartTraceStyle(ChartTraceStyle):  # pylint: disable=too-few-public-methods
    """Trace style for bar charts."""

    def __init__(self) -> None:
        self._use_group_colors = True
        self._color_palette = CHART_PALETTE

    def to_style_dict(self, group_index: Optional[int] = None) -> Dict[str, Any]:
        """Converts the trace style to a dictionary."""
        style = {}
        if self._use_group_colors and group_index is not None:
            color = self._color_palette[group_index % len(self._color_palette)]
            style["marker"] = {"color": color}
        return style


class BarChart(Chart):  # pylint: disable=too-few-public-methods
    """Bar chart component."""

    def __init__(
        self,
        data_frame: pd.DataFrame,
        bar_layout_style: ChartLayoutStyle,
    ) -> None:
        self._data_frame = data_frame
        self._bar_layout_style = bar_layout_style

    def plot(
        self,
        x_col: str,
        y_col: str,
        group_by: Optional[str] = None,
        orientation: str = "v",
    ) -> go.Figure:
        """Plots a bar chart."""
        grouped_data = self._data_frame.groupby(group_by) if group_by else [(None, self._data_frame)]

        fig = go.Figure()

        for idx, (group_name, group_data) in enumerate(grouped_data):
            trace_style = BarChartTraceStyle().to_style_dict(group_index=idx)

            bar_kwargs = {"name": str(group_name) if group_name else y_col, **trace_style}

            if orientation == "v":
                bar_kwargs.update({"x": group_data[x_col], "y": group_data[y_col]})
            else:
                bar_kwargs.update({"x": group_data[y_col], "y": group_data[x_col], "orientation": "h"})

            fig.add_trace(go.Bar(**bar_kwargs))

        fig.update_layout(**self._bar_layout_style.to_layout_dict())

        return fig
