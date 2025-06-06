import dash_bootstrap_components as dbc
from components.atoms.card.card import AlphaCard, AlphaCardBody, AlphaCardHeader
from components.atoms.divider.divider import Divider
from components.atoms.layout.layout import AlphaCol, AlphaRow
from constants import colors
from dash import html
from pages.settings.settings_contants import (
    KEY_SETTINGS_DESCRIPTION_LABEL,
    KEY_SETTINGS_TITLE_LABEL,
    POLYGON_API_KEY_INPUT_ID,
    TRADE_SETTINGS_DESCRIPTION_LABEL,
    TRADE_SETTINGS_TITLE_LABEL,
    TRADE_WINDOW_HOUR_LABEL,
    TRADE_WINDOW_MINUTE_LABEL,
    TRADE_WINDOW_START_HOUR_ID,
    TRADE_WINDOW_START_LABEL,
    TRADE_WINDOW_START_MINUTE_ID,
    TRADE_WINDOW_START_WEEKDAY_ID,
    TRADE_WINDOW_STOP_HOUR_ID,
    TRADE_WINDOW_STOP_LABEL,
    TRADE_WINDOW_STOP_MINUTE_ID,
    TRADE_WINDOW_STOP_WEEKDAY_ID,
    TRADE_WINDOW_WEEKDAY_LABEL,
)
from quant_core.enums.weekday import Weekday


def _render_trade_window() -> html.Div:
    def time_options_24h():
        return [{"label": f"{h:02d}", "value": h} for h in range(24)]

    def minute_options():
        return [{"label": f"{m:02d}", "value": m} for m in range(60)]

    return html.Div(
        children=[
            AlphaRow(
                children=[
                    AlphaCol(html.H5(TRADE_WINDOW_START_LABEL, style={"marginBottom": "1rem"}), xs=12),
                    AlphaCol(
                        children=[
                            dbc.Label(TRADE_WINDOW_WEEKDAY_LABEL),
                            dbc.Select(
                                id=TRADE_WINDOW_START_WEEKDAY_ID,
                                options=[{"label": day.value, "value": day.name} for day in Weekday],
                                placeholder="Select a weekday",
                            ),
                        ],
                        xs=12,
                        sm=6,
                        md=4,
                    ),
                    AlphaCol(
                        children=[
                            dbc.Label(TRADE_WINDOW_HOUR_LABEL),
                            dbc.Select(
                                id=TRADE_WINDOW_START_HOUR_ID,
                                options=time_options_24h(),
                                value="3",
                                placeholder="Select an hour",
                            ),
                        ],
                        xs=6,
                        sm=3,
                        md=2,
                    ),
                    AlphaCol(
                        children=[
                            dbc.Label(TRADE_WINDOW_MINUTE_LABEL),
                            dbc.Select(
                                id=TRADE_WINDOW_START_MINUTE_ID,
                                options=minute_options(),
                                value="00",
                                placeholder="Select a minute",
                            ),
                        ],
                        xs=6,
                        sm=3,
                        md=2,
                    ),
                ],
                style={"marginBottom": "1rem"},
            ),
            Divider(style={"margin": "20px 0px"}).render(),
            AlphaRow(
                children=[
                    AlphaCol(html.H5(TRADE_WINDOW_STOP_LABEL, style={"marginBottom": "1rem"}), xs=12),
                    AlphaCol(
                        children=[
                            dbc.Label(TRADE_WINDOW_WEEKDAY_LABEL),
                            dbc.Select(
                                id=TRADE_WINDOW_STOP_WEEKDAY_ID,
                                options=[{"label": day.value, "value": day.name} for day in Weekday],
                                placeholder="Select a weekday",
                            ),
                        ],
                        xs=12,
                        sm=6,
                        md=4,
                    ),
                    AlphaCol(
                        children=[
                            dbc.Label(TRADE_WINDOW_HOUR_LABEL),
                            dbc.Select(
                                id=TRADE_WINDOW_STOP_HOUR_ID,
                                options=time_options_24h(),
                                placeholder="Select an hour",
                            ),
                        ],
                        xs=6,
                        sm=3,
                        md=2,
                    ),
                    AlphaCol(
                        children=[
                            dbc.Label(TRADE_WINDOW_MINUTE_LABEL),
                            dbc.Select(
                                id=TRADE_WINDOW_STOP_MINUTE_ID,
                                options=minute_options(),
                                placeholder="Select a minute",
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


def render_trade_settings_card() -> html.Div:
    """Render the trade settings card."""
    return html.Div(
        children=[
            AlphaRow(
                AlphaCard(
                    header=AlphaCardHeader(
                        children=[
                            html.H4(TRADE_SETTINGS_TITLE_LABEL),
                            html.P(
                                TRADE_SETTINGS_DESCRIPTION_LABEL,
                                style={"color": colors.TEXT_DISABLED, "marginBottom": "1rem"},
                            ),
                        ]
                    ).render(),
                    body=AlphaCardBody(
                        children=[
                            _render_trade_window(),
                        ]
                    ).render(),
                    style={"backgroundColor": colors.BACKGROUND_WHITE, "marginBottom": "2rem"},
                    show_divider=False,
                ).render(),
            )
        ]
    )


def _render_keys_settings_header() -> html.Div:
    return html.Div(
        [
            html.H4(KEY_SETTINGS_TITLE_LABEL),
            html.P(
                KEY_SETTINGS_DESCRIPTION_LABEL,
                style={"color": colors.TEXT_DISABLED, "marginBottom": "2rem"},
            ),
        ]
    )


def render_keys_settings_card() -> html.Div:
    """Render the keys settings card."""
    return html.Div(
        children=[
            AlphaRow(
                AlphaCard(
                    header=AlphaCardHeader(
                        children=[
                            html.H4(KEY_SETTINGS_TITLE_LABEL),
                            html.P(
                                KEY_SETTINGS_DESCRIPTION_LABEL,
                                style={"color": colors.TEXT_DISABLED, "marginBottom": "1rem"},
                            ),
                        ]
                    ).render(),
                    body=AlphaCardBody(
                        children=[
                            AlphaRow(
                                children=[
                                    AlphaCol(
                                        children=[
                                            dbc.Label("Polygon API Key"),
                                            dbc.Input(
                                                id=POLYGON_API_KEY_INPUT_ID,
                                                type="password",
                                                placeholder="Enter API key",
                                                value="",
                                            ),
                                        ],
                                        xs=12,
                                        sm=8,
                                        md=6,
                                    ),
                                ]
                            ),
                        ]
                    ).render(),
                    style={"backgroundColor": colors.BACKGROUND_WHITE, "marginBottom": "2rem"},
                    show_divider=False,
                ).render()
            )
        ]
    )
