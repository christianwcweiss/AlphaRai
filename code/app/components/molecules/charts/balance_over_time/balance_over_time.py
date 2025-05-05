import pandas as pd
from dash import html, dcc, callback, Input, Output, ctx
import dash_bootstrap_components as dbc
from functools import cache

from components.atoms.buttons.button_group import AlphaButtonGroup
from components.atoms.card.card import AlphaCard, AlphaCardHeader, AlphaCardBody
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.charts.chart import ChartLayoutStyle, ChartMargin
from components.charts.line.line_chart import LineChart
from components.molecules.molecule import Molecule
from quant_core.enums.chart_mode import ChartMode

# IDs
BALANCE_OVER_TIME_MODE_STORE_ID = "balance-over-time_mode-store"
BALANCE_OVER_TIME_ABS_BTN_ID = "balance-over-time_absolute-btn"
BALANCE_OVER_TIME_REL_BTN_ID = "balance-over-time_relative-btn"
BALANCE_OVER_TIME_ABS_DIV_ID = "balance-over-time-abs-div"
BALANCE_OVER_TIME_REL_DIV_ID = "balance-over-time-rel-div"

# Chart wrapper transition styles
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


class BalanceOverTime(Molecule):
    def __init__(self, absolute_df: pd.DataFrame, relative_df: pd.DataFrame):
        self._absolute_df = absolute_df
        self._relative_df = relative_df
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
                        AlphaButtonGroup(
                            group_id="balance-over-time-toggle",
                            buttons=[
                                {"label": "Absolute", "id": BALANCE_OVER_TIME_ABS_BTN_ID, "active": True},
                                {"label": "Relative", "id": BALANCE_OVER_TIME_REL_BTN_ID},
                            ],
                            size="sm"
                        ).render()
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
            id=BALANCE_OVER_TIME_ABS_DIV_ID,
            children=[
                dcc.Graph(
                    figure=LineChart(
                        data_frame=self._absolute_df,
                        line_layout_style=self._chart_layout_style,
                    ).plot(x_col="time", y_col="absolute_balance", group_by="account_id"),
                    config={"displayModeBar": False},
                )
            ],
            style=VISIBLE_STYLE,
        )

    def _render_relative_chart(self):
        return html.Div(
            id=BALANCE_OVER_TIME_REL_DIV_ID,
            children=[
                dcc.Graph(
                    figure=LineChart(
                        data_frame=self._relative_df,
                        line_layout_style=self._chart_layout_style,
                    ).plot(x_col="time", y_col="percentage_growth", group_by="account_id"),
                    config={"displayModeBar": False},
                )
            ],
            style=HIDDEN_STYLE,
        )

    def _render_chart_body(self) -> html.Div:
        return AlphaCardBody(
            children=[
                dcc.Store(id=BALANCE_OVER_TIME_MODE_STORE_ID, data=ChartMode.ABSOLUTE.value),
                AlphaRow(
                    children=[
                        AlphaCol(
                            children=[
                                self._render_absolute_chart(),
                                self._render_relative_chart(),
                            ]
                        )
                    ]
                )
            ]
        ).render()

    @cache
    def render(self) -> html.Div:
        return AlphaCard(
            header=self._render_card_header(),
            body=self._render_chart_body(),
            style={"backgroundColor": "#FFFFFF"},
        ).render()


# ============================
# 🔁 Smooth toggle callback
# ============================

from components.atoms.buttons.button_group import AlphaButtonGroup  # for style reuse

@callback(
    Output(BALANCE_OVER_TIME_ABS_DIV_ID, "style"),
    Output(BALANCE_OVER_TIME_REL_DIV_ID, "style"),
    Output(BALANCE_OVER_TIME_ABS_BTN_ID, "active"),
    Output(BALANCE_OVER_TIME_ABS_BTN_ID, "style"),
    Output(BALANCE_OVER_TIME_REL_BTN_ID, "active"),
    Output(BALANCE_OVER_TIME_REL_BTN_ID, "style"),
    Input(BALANCE_OVER_TIME_ABS_BTN_ID, "n_clicks"),
    Input(BALANCE_OVER_TIME_REL_BTN_ID, "n_clicks"),
    prevent_initial_call=True,
)
def toggle_mode(abs_clicks, rel_clicks):
    triggered = ctx.triggered_id

    if triggered == BALANCE_OVER_TIME_REL_BTN_ID:
        return (
            HIDDEN_STYLE,
            VISIBLE_STYLE,
            False,
            AlphaButtonGroup.DEFAULT_BUTTON_STYLE,
            True,
            AlphaButtonGroup.ACTIVE_BUTTON_STYLE,
        )
    else:
        return (
            VISIBLE_STYLE,
            HIDDEN_STYLE,
            True,
            AlphaButtonGroup.ACTIVE_BUTTON_STYLE,
            False,
            AlphaButtonGroup.DEFAULT_BUTTON_STYLE,
        )
