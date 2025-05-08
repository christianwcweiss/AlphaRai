import pandas as pd
import plotly.graph_objects as go

from components.charts.chart import Chart, ChartLayoutStyle


class HeatmapChart(Chart):
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
        value_col: str,
        aggfunc: str = "sum",
    ) -> go.Figure:
        pivot_df = self._data_frame.pivot_table(
            index=y_col,
            columns=x_col,
            values=value_col,
            aggfunc=aggfunc,
            fill_value=0,
        )

        fig = go.Figure(
            data=go.Heatmap(
                z=pivot_df.values,
                x=pivot_df.columns,
                y=pivot_df.index,
                colorscale="Viridis",
                colorbar=dict(title=value_col),
            )
        )

        fig.update_layout(**self._layout_style.to_layout_dict())
        return fig
