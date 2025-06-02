import pandas as pd
import plotly.graph_objects as go
from components.charts.chart import Chart, ChartLayoutStyle


class HistogramChart(Chart):  # pylint: disable=too-few-public-methods
    """Histogram chart component for visualizing distributions."""

    def __init__(self, data_frame: pd.DataFrame, layout_style: ChartLayoutStyle):
        self._data_frame = data_frame
        self._layout_style = layout_style

    def plot(self, x_col: str, nbins: int = 20) -> go.Figure:
        fig = go.Figure(
            data=[
                go.Histogram(
                    x=self._data_frame[x_col],
                    nbinsx=nbins,
                    marker={"color": "rgba(0, 123, 255, 0.6)"},
                )
            ]
        )
        fig.update_layout(**self._layout_style.to_layout_dict())
        return fig
