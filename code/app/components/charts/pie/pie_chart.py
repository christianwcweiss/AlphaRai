import pandas as pd
import plotly.graph_objects as go

from components.charts.chart import Chart, ChartLayoutStyle
from constants.colors import CHART_PALETTE


class PieChart(Chart):
    def __init__(
        self,
        data_frame: pd.DataFrame,
        layout_style: ChartLayoutStyle,
    ) -> None:
        self._data_frame = data_frame
        self._layout_style = layout_style

    def plot(
        self,
        value_col: str,
        label_col: str,
    ) -> go.Figure:
        colors = CHART_PALETTE[: len(self._data_frame)]

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=self._data_frame[label_col],
                    values=self._data_frame[value_col],
                    marker=dict(colors=colors),
                    hole=0.4,  # optional: donut style
                    sort=False,
                )
            ]
        )

        fig.update_layout(**self._layout_style.to_layout_dict())

        return fig
