from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
from components.charts.chart import Chart, ChartLayoutStyle, ChartTraceStyle
from constants.colors import CHART_PALETTE


class LineChartTraceStyle(ChartTraceStyle):  # pylint: disable=too-few-public-methods
    """Trace style for line charts."""

    def __init__(
        self,
        line_width: Optional[float] = None,
        line_dash: Optional[str] = None,
        show_markers: bool = False,
    ) -> None:
        self._line_width = line_width
        self._line_dash = line_dash
        self._show_markers = show_markers
        self._use_group_colors = True
        self._color_palette = CHART_PALETTE

    def to_style_dict(self, group_index: Optional[int] = None) -> Dict[str, Any]:
        """Converts the trace style to a dictionary for Plotly."""
        style = {"mode": "lines+markers" if self._show_markers else "lines", "line": {}}

        if self._use_group_colors and group_index is not None:
            color = self._color_palette[group_index % len(self._color_palette)]
            style["line"]["color"] = color  # type: ignore

        if self._line_width is not None:
            style["line"]["width"] = self._line_width  # type: ignore
        if self._line_dash is not None:
            style["line"]["dash"] = self._line_dash  # type: ignore

        if not style["line"]:
            style.pop("line")

        return style


class LineChart(Chart):  # pylint: disable=too-few-public-methods
    """Line chart component for visualizing trends over time."""

    def __init__(
        self,
        data_frame: pd.DataFrame,
        line_layout_style: ChartLayoutStyle,
    ) -> None:
        self._data_frame = data_frame
        self._line_layout_style = line_layout_style

    def plot(
        self,
        x_col: str,
        y_col: str,
        group_by: Optional[List[str]] = None,
        daily_last_only: bool = True,
    ) -> go.Figure:
        """Plots a line chart with optional grouping and daily-last-only aggregation."""

        grouped_data = self._data_frame.groupby(group_by) if group_by else [(None, self._data_frame)]

        fig = go.Figure()

        for idx, (group_name, group_data) in enumerate(grouped_data):
            group_data = group_data.sort_values(x_col)

            if daily_last_only:
                group_data["_date"] = pd.to_datetime(group_data[x_col]).dt.date
                group_data.sort_values(["_date"], inplace=True)
                group_data = group_data.groupby("_date").tail(1)

            if isinstance(group_name, tuple):
                name = " | ".join(map(str, group_name))
            elif group_name is not None:
                name = str(group_name)
            else:
                name = y_col

            trace_style = LineChartTraceStyle().to_style_dict(group_index=idx)

            fig.add_trace(
                go.Scatter(
                    x=group_data[x_col],
                    y=group_data[y_col],
                    name=f"{name} - {y_col}",
                    showlegend=True,
                    **trace_style,
                )
            )

        fig.update_layout(**self._line_layout_style.to_layout_dict())

        return fig
