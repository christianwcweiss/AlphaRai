import plotly.graph_objects as go
from components.charts.chart import Chart, ChartLayoutStyle


class GaugeChart(Chart):  # pylint: disable=too-few-public-methods
    """Gauge chart component."""

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        value: float,
        title: str,
        layout_style: ChartLayoutStyle,
        min_val: float = 0,
        max_val: float = 100,
    ):
        self._value = value
        self._title = title
        self._layout_style = layout_style
        self._min_val = min_val
        self._max_val = max_val

    def plot(self) -> go.Figure:
        """Plots a gauge chart."""
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=self._value,
                title={"text": self._title},
                gauge={
                    "axis": {"range": [self._min_val, self._max_val]},
                    "bar": {"color": "rgba(0, 123, 255, 0.7)"},
                    "steps": [
                        {"range": [self._min_val, self._max_val * 0.5], "color": "lightgray"},
                        {"range": [self._max_val * 0.5, self._max_val * 0.8], "color": "gray"},
                        {"range": [self._max_val * 0.8, self._max_val], "color": "green"},
                    ],
                },
            )
        )

        fig.update_layout(**self._layout_style.to_layout_dict())
        return fig
