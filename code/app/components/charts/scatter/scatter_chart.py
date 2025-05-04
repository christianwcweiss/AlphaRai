from typing import Optional

import pandas as pd
import plotly.graph_objects as go

from components.charts.chart import Chart, ChartLayoutStyle
from constants.colors import CHART_PALETTE


class ScatterChart(Chart):
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
        size_col: Optional[str] = None,
    ) -> go.Figure:
        fig = go.Figure()

        grouped = self._data_frame.groupby(group_by) if group_by else [(None, self._data_frame)]

        for idx, (group_name, group_data) in enumerate(grouped):
            color = CHART_PALETTE[idx % len(CHART_PALETTE)]

            scatter_args = dict(
                x=group_data[x_col],
                y=group_data[y_col],
                name=str(group_name) if group_name else y_col,
                mode="markers",
                marker=dict(
                    size=group_data[size_col] if size_col else 8,
                    color=color,
                    opacity=0.7,
                ),
            )

            fig.add_trace(go.Scatter(**scatter_args))

        fig.update_layout(**self._layout_style.to_layout_dict())
        return fig
