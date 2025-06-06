from typing import List

import pandas as pd
from components.atoms.card.card import AlphaCard, AlphaCardBody, AlphaCardHeader
from components.atoms.layout.layout import AlphaCol, AlphaRow
from components.charts.chart import ChartLayoutStyle, ChartMargin
from components.charts.line.line_chart import LineChart
from components.molecules.molecule import Molecule
from dash import dcc, html
from quant_core.enums.chart_mode import ChartMode

BALANCE_OVER_TIME_MODE_STORE_ID = "balance-over-time_mode-store"
BALANCE_OVER_TIME_ABS_BTN_ID = "balance-over-time_absolute-btn"
BALANCE_OVER_TIME_REL_BTN_ID = "balance-over-time_relative-btn"
BALANCE_OVER_TIME_ABS_DIV_ID = "balance-over-time-abs-div"
BALANCE_OVER_TIME_REL_DIV_ID = "balance-over-time-rel-div"


class BalanceOverTimeMolecule(Molecule):  # pylint: disable=too-few-public-methods
    """A molecule that renders the Balance Over Time chart."""

    def __init__(self, data_frame: pd.DataFrame):
        self._data_frame = data_frame
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

    def _render_card_header(self) -> html.Div:
        return AlphaCardHeader(
            children=[
                html.Div(
                    children=[
                        html.H5("BALANCE OVER TIME"),
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

    def _render_absolute_chart(self, groups: List[str]) -> html.Div:
        return html.Div(
            id=BALANCE_OVER_TIME_ABS_DIV_ID,
            children=[
                dcc.Graph(
                    figure=LineChart(
                        data_frame=self._data_frame,
                        line_layout_style=self._chart_layout_style,
                    ).plot(x_col="closed_at", y_col="absolute_balance", group_by=groups),
                    config={"displayModeBar": True},
                )
            ],
        )

    def _render_relative_chart(self, groups: List[str]) -> html.Div:
        return html.Div(
            id=BALANCE_OVER_TIME_REL_DIV_ID,
            children=[
                dcc.Graph(
                    figure=LineChart(
                        data_frame=self._data_frame,
                        line_layout_style=self._chart_layout_style,
                    ).plot(x_col="closed_at", y_col="relative_balance", group_by=groups),
                    config={"displayModeBar": True},
                )
            ],
        )

    def _render_chart_body(self, groups: List[str], chart_mode: ChartMode) -> html.Div:
        return AlphaCardBody(
            children=[
                dcc.Store(id=BALANCE_OVER_TIME_MODE_STORE_ID, data=ChartMode.ABSOLUTE.value),
                AlphaRow(
                    children=[
                        AlphaCol(
                            children=[
                                (
                                    self._render_absolute_chart(groups=groups)
                                    if chart_mode is ChartMode.ABSOLUTE
                                    else self._render_relative_chart(groups=groups)
                                ),
                            ]
                        )
                    ]
                ),
            ]
        ).render()

    def render(self, groups: List[str], chart_mode: ChartMode) -> html.Div:
        """Render the molecule."""
        return AlphaCard(
            header=self._render_card_header(),
            body=self._render_chart_body(groups=groups, chart_mode=chart_mode),
            style={"backgroundColor": "#FFFFFF"},
        ).render()
