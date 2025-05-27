from typing import Optional

import pandas as pd
import plotly.graph_objects as go

from components.charts.chart import Chart, ChartLayoutStyle
from constants.colors import CHART_PALETTE


class StackedAreaChart(Chart):  # pylint: disable=too-few-public-methods
    """Stacked area chart component."""

    def __init__(
        self,
        data_frame: pd.DataFrame,
        layout_style: ChartLayoutStyle,
    ) -> None:
        self._data_frame = data_frame
        self._layout_style = layout_style

    def plot(
        self,
        x_col: str,
        y_col: str,
        group_by: Optional[str] = None,
    ) -> go.Figure:
        grouped_data = self._data_frame.groupby(group_by) if group_by else [(None, self._data_frame)]

        fig = go.Figure()

        for idx, (group_name, group_data) in enumerate(grouped_data):
            color = CHART_PALETTE[idx % len(CHART_PALETTE)]

            fig.add_trace(
                go.Scatter(
                    x=group_data[x_col],
                    y=group_data[y_col],
                    mode="lines",
                    name=str(group_name) if group_name else y_col,
                    stackgroup="one",
                    line={"width": 0.5, "color": color},
                    groupnorm="",
                )
            )

        fig.update_layout(**self._layout_style.to_layout_dict())

        return fig
