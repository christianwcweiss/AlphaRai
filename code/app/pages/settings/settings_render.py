import dash_bootstrap_components as dbc
from components.atoms.layout.layout import AlphaCol, AlphaRow
from constants import colors
from dash import html
from pages.settings.settings_contants import ORDER_RETENTION_PERIOD_LABEL
from quant_core.enums.weekday import Weekday


def _render_trade_settings_header() -> html.Div:
    return html.Div(
        children=[
            html.H5("Trade Settings"),
            html.P(
                "This section contains settings related to trading operations.",
                style={"color": colors.TEXT_DISABLED},
            ),
        ]
    )


def _render_order_retention_period_content() -> html.Div:
    return html.Div(
        AlphaRow(
            children=[
                AlphaCol(
                    children=[
                        dbc.Label(ORDER_RETENTION_PERIOD_LABEL),
                        dbc.Input(
                            id="test",
                            type="number",
                            value=300,
                            min=0,
                            step=1,
                            placeholder="Enter retention period in minutes",
                        ),
                    ]
                ),
            ]
        ),
    )


def _render_default_account_config_settings_content() -> html.Div:
    pass


def _render_trade_window() -> html.Div:
    def time_options_24h():
        return [{"label": f"{h:02d}", "value": h} for h in range(24)]

    def minute_options():
        return [{"label": f"{m:02d}", "value": m} for m in range(60)]

    return html.Div(
        children=[
            html.P("Trade Window"),
            AlphaRow(
                children=[
                    AlphaCol(
                        children=[
                            dbc.Label("Open From – Day"),
                            dbc.Select(
                                id="trade-window-start-day",
                                options=[{"label": day.value, "value": day.name} for day in Weekday],
                                value=Weekday.MONDAY.name,
                            ),
                        ],
                        xs=12,
                        sm=6,
                        md=4,
                    ),
                    AlphaCol(
                        children=[
                            dbc.Label("Hour"),
                            dbc.Select(
                                id="trade-window-start-hour",
                                options=time_options_24h(),
                                value="3",
                            ),
                        ],
                        xs=6,
                        sm=3,
                        md=2,
                    ),
                    AlphaCol(
                        children=[
                            dbc.Label("Minute"),
                            dbc.Select(
                                id="trade-window-start-minute",
                                options=minute_options(),
                                value="00",
                            ),
                        ],
                        xs=6,
                        sm=3,
                        md=2,
                    ),
                ],
                style={"marginBottom": "1rem"},
            ),
            AlphaRow(
                children=[
                    AlphaCol(
                        children=[
                            dbc.Label("Close At – Day"),
                            dbc.Select(
                                id="trade-window-end-day",
                                options=[{"label": day.value, "value": day.name} for day in Weekday],
                                value=Weekday.FRIDAY.name,
                            ),
                        ],
                        xs=12,
                        sm=6,
                        md=4,
                    ),
                    AlphaCol(
                        children=[
                            dbc.Label("Hour"),
                            dbc.Select(
                                id="trade-window-end-hour",
                                options=time_options_24h(),
                                value="21",
                            ),
                        ],
                        xs=6,
                        sm=3,
                        md=2,
                    ),
                    AlphaCol(
                        children=[
                            dbc.Label("Minute"),
                            dbc.Select(
                                id="trade-window-end-minute",
                                options=minute_options(),
                                value="00",
                            ),
                        ],
                        xs=6,
                        sm=3,
                        md=2,
                    ),
                ]
            ),
        ]
    )


def _render_trade_settings_content() -> html.Div:
    return html.Div(children=[_render_order_retention_period_content(), _render_trade_window()])


def render_trade_settings_row() -> html.Div:
    """Render the trade settings row."""
    return html.Div(
        [
            _render_trade_settings_header(),
            _render_trade_settings_content(),
        ]
    )


def render_keys_settings_row() -> html.Div:
    """Render the trade settings row."""
    return html.Div(
        [
            html.H5("KEYS"),
            html.P(
                "This section contains settings related to keys for external APIs.",
                style={"color": colors.TEXT_DISABLED},
            ),
        ]
    )
