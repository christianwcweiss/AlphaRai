from typing import List, Optional, Dict

import pandas as pd

import plotly.graph_objects as go

from components.atoms.charts.chart import Chart, ChartStyle, ChartMargin


class LineChartStyle(ChartStyle):
    def __init__(
            self,
            title: str,
            x_axis_title: str,
            x_axis_title_show: bool,
            x_grid_show: bool,
            y_axis_title: str,
            y_axis_title_show: bool,
            y_grid_show: bool,
            show_legend: bool,
            margin: ChartMargin,
    ) -> None:
        self._title = title
        self._x_axis_title = x_axis_title
        self._x_grid_show = x_grid_show
        self._y_axis_title = y_axis_title
        self._y_grid_show = y_grid_show
        self._show_legend = show_legend
        self._margin = margin

    def to_style_dict(self) -> Dict[str, any]:
        style_dict = {
            "title": {
                "text": self._title,
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 24, "family": "Arial, sans-serif"}
            },
            "xaxis": {
                "title": self._x_axis_title,
                "showgrid": self._x_grid_show,
                "gridcolor": "rgba(200,200,200,0.3)",
                "zeroline": False,
                "tickfont": {"size": 14},
                "titlefont": {"size": 18}
            },
            "yaxis": {
                "title": self._y_axis_title,
                "showgrid": self._y_grid_show,
                "gridcolor": "rgba(200,200,200,0.3)",
                "zeroline": False,
                "tickfont": {"size": 14},
                "titlefont": {"size": 18}
            },
            "plot_bgcolor": "white",
            "paper_bgcolor": "white",
            "margin": self._margin.margins
        }

        if self._show_legend:
            style_dict["legend"] = {
                "orientation": "h",
                "yanchor": 'bottom',
                "y": -0.2,
                "xanchor": 'center',
                "x": 0.5,
                "font": {"size": 14}
            }

        return style_dict


class LineChart(Chart):
    def __init__(
        self,
        data_frame: pd.DataFrame,
    ) -> None:
        self._data_frame = data_frame

    def plot(
        self,
        x_col: str,
        y_col: str,
        group_by: Optional[str] = None,
        line_chart_style: Optional[LineChartStyle] = None,
    ) -> go.Figure:
        grouped_data = self._data_frame.groupby(group_by) if group_by else [(None, self._data_frame)]

        fig = go.Figure()

        for group_name, group_data in grouped_data:
            fig.add_trace(
                go.Scatter(
                    x=group_data[x_col],
                    y=group_data[y_col],
                    mode="lines",
                    name=f"{group_name} - {y_col}" if group_name else y_col,
                )
            )

        fig.update_layout(**line_chart_style.to_style_dict())

        return fig
