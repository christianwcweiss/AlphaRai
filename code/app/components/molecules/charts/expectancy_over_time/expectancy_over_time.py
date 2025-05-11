from functools import cache

import pandas as pd
from dash import html, dcc, callback, Input, Output, ctx

from components.atoms.buttons.general.button_group import AlphaButtonGroup
from components.atoms.card.card import AlphaCard, AlphaCardHeader, AlphaCardBody
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.charts.chart import ChartLayoutStyle, ChartMargin
from components.charts.line.line_chart import LineChart
from components.molecules.molecule import Molecule

# IDs
EXPECTANCY_MODE_STORE_ID = "expectancy-mode-store"
EXPECTANCY_ABS_BTN_ID = "expectancy-absolute-btn"
EXPECTANCY_REL_BTN_ID = "expectancy-relative-btn"
EXPECTANCY_ABS_DIV_ID = "expectancy-absolute-div"
EXPECTANCY_REL_DIV_ID = "expectancy-relative-div"

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


class ExpectancyOverTime(Molecule):
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
            margin=ChartMargin(10, 10, 10, 10),
        )

    def _render_card_header(self):
        return AlphaCardHeader(
            [
                html.Div(
                    [
                        html.H5("EXPECTANCY OVER TIME"),
                        AlphaButtonGroup(
                            group_id="expectancy-toggle",
                            buttons=[
                                {"label": "Absolute", "id": EXPECTANCY_ABS_BTN_ID, "active": True},
                                {"label": "Relative", "id": EXPECTANCY_REL_BTN_ID},
                            ],
                            size="sm",
                        ).render(),
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
            id=EXPECTANCY_ABS_DIV_ID,
            children=[
                dcc.Graph(
                    figure=LineChart(
                        data_frame=self._absolute_df,
                        line_layout_style=self._chart_layout_style,
                    ).plot(x_col="time", y_col="expectancy", group_by="account_id"),
                    config={"displayModeBar": False},
                )
            ],
            style=VISIBLE_STYLE,
        )

    def _render_relative_chart(self):
        return html.Div(
            id=EXPECTANCY_REL_DIV_ID,
            children=[
                dcc.Graph(
                    figure=LineChart(
                        data_frame=self._relative_df,
                        line_layout_style=self._chart_layout_style,
                    ).plot(x_col="time", y_col="expectancy_pct", group_by="account_id"),
                    config={"displayModeBar": False},
                )
            ],
            style=HIDDEN_STYLE,
        )

    def _render_chart_body(self):
        return AlphaCardBody(
            [
                dcc.Store(id=EXPECTANCY_MODE_STORE_ID, data="absolute"),
                AlphaRow([AlphaCol([self._render_absolute_chart(), self._render_relative_chart()])]),
            ]
        ).render()

    @cache
    def render(self) -> html.Div:
        return AlphaCard(
            header=self._render_card_header(),
            body=self._render_chart_body(),
            style={"backgroundColor": "#FFFFFF"},
        ).render()


@callback(
    Output(EXPECTANCY_ABS_DIV_ID, "style"),
    Output(EXPECTANCY_REL_DIV_ID, "style"),
    Output(EXPECTANCY_ABS_BTN_ID, "active"),
    Output(EXPECTANCY_ABS_BTN_ID, "style"),
    Output(EXPECTANCY_REL_BTN_ID, "active"),
    Output(EXPECTANCY_REL_BTN_ID, "style"),
    Input(EXPECTANCY_ABS_BTN_ID, "n_clicks"),
    Input(EXPECTANCY_REL_BTN_ID, "n_clicks"),
    prevent_initial_call=True,
)
def toggle_expectancy_mode(_, __):
    triggered = ctx.triggered_id
    from components.atoms.buttons.general.button_group import AlphaButtonGroup

    if triggered == EXPECTANCY_REL_BTN_ID:
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
