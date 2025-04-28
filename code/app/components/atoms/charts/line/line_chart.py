from typing import Optional, Dict, Any

import pandas as pd
import plotly.graph_objects as go

from components.atoms.charts.chart import Chart, ChartTraceStyle, ChartLayoutStyle
from constants.colors import CHART_PALETTE


class LineChartTraceStyle(ChartTraceStyle):
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
        style = {"mode": "lines+markers" if self._show_markers else "lines", "line": {}}

        # Dynamically assign a color if needed
        if self._use_group_colors and group_index is not None:
            color = self._color_palette[group_index % len(self._color_palette)]
            style["line"]["color"] = color

        if self._line_width is not None:
            style["line"]["width"] = self._line_width
        if self._line_dash is not None:
            style["line"]["dash"] = self._line_dash

        if not style["line"]:
            style.pop("line")

        return style


class LineChart(Chart):
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
        group_by: Optional[str] = None,
    ) -> go.Figure:
        grouped_data = self._data_frame.groupby(group_by) if group_by else [(None, self._data_frame)]

        fig = go.Figure()

        for idx, (group_name, group_data) in enumerate(grouped_data):
            trace_style = LineChartTraceStyle().to_style_dict(group_index=idx)

            fig.add_trace(
                go.Scatter(
                    x=group_data[x_col],
                    y=group_data[y_col],
                    name=f"{group_name} - {y_col}" if group_name else y_col,
                    showlegend=True,
                    **trace_style,
                )
            )

        fig.update_layout(**self._line_layout_style.to_layout_dict())

        return fig
