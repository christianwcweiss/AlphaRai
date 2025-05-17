import pandas as pd
from dash import html, dcc

from components.atoms.card.card import AlphaCard, AlphaCardHeader, AlphaCardBody
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.charts.chart import ChartLayoutStyle, ChartMargin
from components.charts.line.line_chart import LineChart
from components.molecules.molecule import Molecule

# IDs
PF_MODE_STORE_ID = "profit-factor-mode-store"
PF_ABS_DIV_ID = "profit-factor-absolute-div"

VISIBLE_STYLE = {
    "opacity": 1,
    "height": "auto",
    "pointerEvents": "auto",
    "transition": "opacity 0.3s ease-in-out",
}
HIDDEN_STYLE = {
    "opacity": 0,
    "height": 0,
    "overflow": "hidden",
    "pointerEvents": "none",
    "transition": "opacity 0.3s ease-in-out",
}


class ProfitFactorOverTimeMolecule(Molecule):  # pylint: disable=too-few-public-methods
    """A molecule that renders the Profit Factor Over Time chart."""

    def __init__(self, absolute_df: pd.DataFrame) -> None:
        self._data_frame = absolute_df
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
                    [
                        html.H5("PROFIT FACTOR OVER TIME"),
                    ],
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

    def _render_absolute_chart(self):
        return html.Div(
            id=PF_ABS_DIV_ID,
            children=[
                dcc.Graph(
                    figure=LineChart(
                        data_frame=self._data_frame,
                        line_layout_style=self._chart_layout_style,
                    ).plot(x_col="time", y_col="profit_factor", group_by="account_id"),
                    config={"displayModeBar": False},
                )
            ],
            style=VISIBLE_STYLE,
        )

    def _render_chart_body(self):
        return AlphaCardBody(
            [
                dcc.Store(id=PF_MODE_STORE_ID, data="absolute"),
                AlphaRow([AlphaCol([self._render_absolute_chart()])]),
            ]
        ).render()

    def render(self) -> html.Div:
        return AlphaCard(
            header=self._render_card_header(),
            body=self._render_chart_body(),
            style={"backgroundColor": "#FFFFFF"},
        ).render()
