import pandas as pd
from dash import html, dcc

from components.atoms.card.card import AlphaCard, AlphaCardHeader, AlphaCardBody
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.charts.chart import ChartLayoutStyle, ChartMargin
from components.charts.line.line_chart import LineChart
from components.molecules.molecule import Molecule


class AvgTradeDurationOverTimeMolecule(Molecule):  # pylint: disable=too-few-public-methods
    """A molecule that renders the Average Trade Duration Over Time chart."""

    def __init__(self, duration_df: pd.DataFrame):
        self._df = duration_df
        self._chart_layout_style = ChartLayoutStyle(
            title="",
            x_axis_title="",
            y_axis_title="",
            show_legend=False,
            show_title=False,
            show_x_title=False,
            show_y_title=False,
            margin=ChartMargin(top=10, right=10, bottom=10, left=10),
        )

    def _render_chart(self) -> dcc.Graph:
        return dcc.Graph(
            figure=LineChart(
                data_frame=self._df,
                line_layout_style=self._chart_layout_style,
            ).plot(x_col="time", y_col="avg_duration_min", group_by="account_id"),
            config={"displayModeBar": False},
        )

    def render(self) -> html.Div:
        """Renders the molecule."""
        return AlphaCard(
            header=AlphaCardHeader([html.H5("AVG TRADE DURATION OVER TIME")]).render(),
            body=AlphaCardBody([AlphaRow([AlphaCol([self._render_chart()])])]).render(),
            style={"backgroundColor": "#FFFFFF"},
        ).render()
