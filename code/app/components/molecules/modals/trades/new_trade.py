from typing import List

from dash import html, dcc, Input, Output, State, callback, dash
import dash_bootstrap_components as dbc

from components.molecules.molecule import Molecule
from constants import colors
from components.atoms.buttons.general.button import AlphaButton
from constants.style import HIDDEN
from services.trade_parser import TradeMessageParser
from entities.trade_details import TradeDetails
from services.trade_router import TradeRouter
from quant_core.services.core_logger import CoreLogger


def render_trade_input_text_area() -> html.Div:
    return html.Div(
        [
            dcc.Textarea(
                id="trade-input-text-area",
                style={"width": "100%", "height": "500px", "display": "block"},
                placeholder="Paste signal here...",
            ),
            html.Br(),
            AlphaButton("Parse Signal", "parse-trade-btn").render(),
            html.Br(),
        ],
        id="trade-input-container",
        style={"marginBottom": "1rem"},
    )

def render_trade_details_section() -> List[html.Div]:
    return [html.Div(
            [
                html.H6("📋 Trade Details", className="fw-bold mb-2"),
                html.Div(
                    id="parsed-trade-output",
                    style={
                        "backgroundColor": "#f8f9fa",
                        "padding": "1rem",
                        "borderRadius": "0.5rem",
                        "boxShadow": "0 2px 6px rgba(0,0,0,0.05)",
                    },
                ),
            ],
            id="trade-details-section",
            style={"marginBottom": "1.5rem", "display": "none"},
        ),
        html.Div(
            [
                html.H6("🧠 Confluences", className="fw-bold mb-2"),
                html.Div("(To be implemented...)", className="text-muted"),
            ],
            id="confluence-section",
            style={"marginBottom": "1.5rem", "display": "none"},
        ),
        html.Div(
            [
                html.H6("⚖️ Risk Overview", className="fw-bold mb-2"),
                html.Div("(To be implemented...)", className="text-muted"),
            ],
            id="risk-section",
            style={"marginBottom": "1.5rem", "display": "none"},
        ),
        html.Div(
            [
                AlphaButton("Execute Trade", "submit-trade-btn", style={"display": "none"}).render(),
            ]
        )]

class NewTradeModal(Molecule):
    def render(self) -> dbc.Modal:
        return dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("New Trade")),
                dbc.ModalBody(
                    [
                        render_trade_input_text_area(),
                        *render_trade_details_section()
                    ],
                    style={"maxHeight": "60vh", "overflowY": "auto"},
                ),
                dbc.ModalFooter([AlphaButton("Close", "close-trade-modal-btn").render()]),
            ],
            id="new-trade-modal",
            is_open=False,
            size="xl",
            keyboard=False,
            backdrop="static",
        )


@callback(
    Output("new-trade-modal", "is_open"),
    Output("trade-input-text-area", "value", allow_duplicate=True),
    Output("parsed-trade-output", "children", allow_duplicate=True),
    Output("parsed-trade-store", "data", allow_duplicate=True),
    Output("submit-trade-btn", "style", allow_duplicate=True),
    Output("trade-input-container", "style", allow_duplicate=True),
    Output("trade-details-section", "style", allow_duplicate=True),
    Output("confluence-section", "style", allow_duplicate=True),
    Output("risk-section", "style", allow_duplicate=True),
    [
        Input("open-trade-modal-btn", "n_clicks"),
        Input("close-trade-modal-btn", "n_clicks"),
    ],
    State("new-trade-modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_trade_modal(open_click, close_click, is_open):
    return (
        not is_open,
        "",
        None,
        None,
        HIDDEN,
        {"marginBottom": "1rem", "display": "block"},
        {"marginBottom": "1.5rem", "display": "none"},
        {"marginBottom": "1.5rem", "display": "none"},
        {"marginBottom": "1.5rem", "display": "none"},
    )


@callback(
    Output("parsed-trade-output", "children", allow_duplicate=True),
    Output("parsed-trade-store", "data", allow_duplicate=True),
    Output("submit-trade-btn", "style", allow_duplicate=True),
    Output("trade-input-container", "style", allow_duplicate=True),
    Output("trade-details-section", "style", allow_duplicate=True),
    Output("confluence-section", "style", allow_duplicate=True),
    Output("risk-section", "style", allow_duplicate=True),
    Input("parse-trade-btn", "n_clicks"),
    State("trade-input-text-area", "value"),
    prevent_initial_call=True,
)
def parse_trade_signal(_, signal_input):
    if not signal_input:
        return (
            dbc.Alert("Please paste a signal...", color=colors.WARNING_COLOR),
            dash.no_update,
            HIDDEN,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )
    try:
        trade_details = TradeMessageParser.parse(signal_input)
    except Exception as e:
        CoreLogger().error(f"Failed to parse signal: {e}")
        return (
            dbc.Alert(f"Error parsing signal: {e}", color=colors.ERROR_COLOR),
            dash.no_update,
            HIDDEN,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    preview = html.Ul(
        [
            html.Li(f"🎯 Symbol: {trade_details.symbol}"),
            html.Li(f"↕️ Direction: {trade_details.direction.normalize().value.capitalize()}"),
            html.Li(f"⏱️ Timeframe: {trade_details.timeframe}"),
            html.Li(f"💰 Entry: {trade_details.entry}"),
            html.Li(f"🚩 SL: {trade_details.stop_loss}"),
            html.Li(f"🎯 TP1: {trade_details.take_profit_1}"),
            html.Li(f"🎯 TP2: {trade_details.take_profit_2 or '–'}"),
            html.Li(f"🎯 TP3: {trade_details.take_profit_3 or '–'}"),
            html.Li(f"🤖 Confidence: {trade_details.ai_confidence or '–'}%"),
        ],
        style={"paddingLeft": "1.2rem"},
    )

    return (
        preview,
        trade_details.to_dict(),
        AlphaButton.DEFAULT_STYLE,
        {"display": "none"},
        {"marginBottom": "1.5rem", "display": "block"},
        {"marginBottom": "1.5rem", "display": "block"},
        {"marginBottom": "1.5rem", "display": "block"},
    )


@callback(
    Output("trade-status", "children"),
    Input("submit-trade-btn", "n_clicks"),
    State("parsed-trade-store", "data"),
    prevent_initial_call=True,
)
def execute_trade(_, trade_data):
    try:
        CoreLogger().info(f"Routing Trade: {trade_data}")
        trade = TradeDetails(**trade_data)
        TradeRouter(trade).route_trade()

        return dbc.Alert("✅ Trade successfully routed!", color=colors.SUCCESS_COLOR, dismissable=True)
    except Exception as e:
        CoreLogger().error(f"Execution failed: {e}")

        return dbc.Alert(f"Trade execution failed: {e}", color=colors.ERROR_COLOR, dismissable=True)
