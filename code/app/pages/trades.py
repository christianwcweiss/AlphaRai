from typing import Tuple, Any, Dict, Union

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback

from components.atoms.buttons.button import AlphaButton
from components.atoms.content import MainContent
from components.atoms.text.page import PageHeader
from components.atoms.text.section import SectionHeader
from components.frame.body import PageBody
from constants import colors
from constants.style import HIDDEN
from entities.trade_details import TradeDetails
from pages.base_page import BasePage
from quant_core.services.core_logger import CoreLogger
from services.trade_parser import TradeMessageParser
from services.trade_router import TradeRouter

dash.register_page(__name__, path="/trades", name="Trades")


class TradesPage(BasePage):
    def render(self):
        return PageBody(
            [
                PageHeader(self._title),
                MainContent(
                    [
                        SectionHeader(title="Paste Trade Signal").render(),
                        dbc.Row(
                           dbc.Col(
                               dcc.Textarea(
                                   id="signal-input-text-area",
                                   style={"width": "100%", "height": "300px"},
                                   placeholder="Paste signal here...",
                               ),
                               xs=12,
                             sm=12,
                                md=12,
                                lg=12,
                                xl=12,
                           )
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    AlphaButton(label="Parse Signal", id="parse-trade-btn").render(),
                                    xs=12,
                                    sm=12,
                                    md=4,
                                    lg=4,
                                    xl=4,
                                ),
                                dbc.Col(
                                    AlphaButton(label="Clear", id="clear-trade-btn").render(),
                                    xs=12,
                                    sm=12,
                                    md=4,
                                    lg=4,
                                    xl=4,
                                ),
                                dbc.Col(
                                    AlphaButton(
                                        label="Execute Trade",
                                        id="submit-trade-btn",
                                        style=HIDDEN,
                                    ).render(),
                                    xs=12,
                                    sm=12,
                                    md=4,
                                    lg=4,
                                    xl=4,
                                ),
                            ],
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div(id="parsed-trade-output"),
                                    xs=12,
                                    sm=12,
                                    md=12,
                                    lg=12,
                                    xl=12,
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div(id="trade-status"),
                                    xs=12,
                                    sm=12,
                                    md=12,
                                    lg=12,
                                    xl=12,
                                ),
                            ]
                        ),
                        dcc.Store(id="parsed-trade-store"),
                    ]
                ),
            ]
        )


layout = TradesPage(title="Trades").layout


@callback(
    Output("parsed-trade-output", "children", allow_duplicate=True),
    Output("parsed-trade-store", "data", allow_duplicate=True),
    Output("submit-trade-btn", "style", allow_duplicate=True),
    Input("parse-trade-btn", "n_clicks"),
    State("signal-input-text-area", "value"),
    prevent_initial_call=True,
)
def parse_trade_signal(_, signal_input: str) -> Union[Tuple[dbc.Alert, Any, Dict[str, Any]], Tuple[html.Ul, Dict[str, Any], Dict[str, Any]]]:
    if not signal_input:
        return dbc.Alert("Please paste a signal...", color=colors.WARNING_COLOR), dash.no_update, HIDDEN

    try:
        trade_details = TradeMessageParser.parse(signal_input)
        preview = html.Ul(
            [
                html.Li(f"Symbol: {trade_details.symbol}"),
                html.Li(f"Direction: {trade_details.direction}"),
                html.Li(f"Timeframe: {trade_details.timeframe}"),
                html.Li(f"Entry: {trade_details.entry}"),
                html.Li(f"Stop Loss: {trade_details.stop_loss}"),
                html.Li(f"Take Profit 1: {trade_details.take_profit_1}"),
                html.Li(f"Take Profit 2: {trade_details.take_profit_2 or '-'}"),
                html.Li(f"Take Profit 3: {trade_details.take_profit_3 or '-'}"),
                html.Li(f"AI Confidence: {trade_details.ai_confidence or '-'}%"),
            ]
        )

        return preview, trade_details.to_dict(), {"display": "inline-block"}

    except Exception as e:
        CoreLogger().error(f"Failed to parse signal: {e}")
        return dbc.Alert(f"Error parsing signal: {e}", color=colors.ERROR_COLOR), dash.no_update, HIDDEN


@callback(
    Output("signal-input-text-area", "value", allow_duplicate=True),
    Output("parsed-trade-output", "children", allow_duplicate=True),
    Output("parsed-trade-store", "data", allow_duplicate=True),
    Output("submit-trade-btn", "style", allow_duplicate=True),
    Input("clear-trade-btn", "n_clicks"),
    prevent_initial_call=True,
)
def clear_trade_ui(_):
    return "", None, None, HIDDEN


@callback(
    Output("trade-status", "children"),
    Input("submit-trade-btn", "n_clicks"),
    State("parsed-trade-store", "data"),
    prevent_initial_call=True,
)
def execute_trade(_, trade_data: Dict[str, Any]):
    try:
        CoreLogger().info(f"Routing Trade: {trade_data}")
        trade = TradeDetails(**trade_data)

        TradeRouter(trade).route_trade()

        return dbc.Alert("✅ Trade successfully routed!", color=colors.SUCCESS_COLOR, dismissable=True)
    except Exception as e:
        CoreLogger().error(f"Execution failed: {e}")
        return dbc.Alert(f"Trade execution failed: {e}", color=colors.ERROR_COLOR, dismissable=True)
