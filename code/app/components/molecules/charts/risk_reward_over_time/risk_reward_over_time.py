import pandas as pd
from components.atoms.card.card import AlphaCard, AlphaCardBody, AlphaCardHeader
from components.atoms.layout.layout import AlphaCol, AlphaRow
from components.charts.chart import ChartLayoutStyle, ChartMargin
from components.charts.line.line_chart import LineChart
from components.molecules.molecule import Molecule
from dash import dcc, html

# Chart Style
VISIBLE_STYLE = {
    "opacity": 1,
    "height": "auto",
    "pointerEvents": "auto",
    "transition": "opacity 0.3s ease-in-out",
}


class RiskRewardOverTimeMolecule(Molecule):  # pylint: disable=too-few-public-methods
    """A molecule that renders the Risk-Reward Over Time chart."""

    def __init__(self, df: pd.DataFrame):
        self._df = df
        self._chart_layout_style = ChartLayoutStyle(
            title="",
            x_axis_title="",
            y_axis_title="",
            show_legend=False,
            show_title=False,
            show_x_title=False,
            show_y_title=False,
            margin=ChartMargin(10, 10, 10, 10),
        )

    def _render_card_header(self):
        return AlphaCardHeader(
            [
                html.Div(
                    [html.H5("RISK-REWARD OVER TIME")],
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center",
                        "width": "100%",
                        "paddingLeft": "10px",
                        "paddingRight": "10px",
                    },
                )
            ]
        ).render()

    def _render_chart(self):
        return html.Div(
            children=[
                dcc.Graph(
                    figure=LineChart(
                        data_frame=self._df,
                        line_layout_style=self._chart_layout_style,
                    ).plot(x_col="time", y_col="risk_reward", group_by="account_id"),
                    config={"displayModeBar": False},
                )
            ],
            style=VISIBLE_STYLE,
        )

    def _render_chart_body(self):
        return AlphaCardBody([AlphaRow([AlphaCol([self._render_chart()])])]).render()

    def render(self) -> html.Div:
        return AlphaCard(
            header=self._render_card_header(),
            body=self._render_chart_body(),
            style={"backgroundColor": "#FFFFFF"},
        ).render()
