import dash
from dash import html, dcc, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc

from components.atoms.content import MainContent
from components.atoms.header import PageHeader
from components.frame.body import PageBody
from pages.base_page import BasePage
from quant_core.services.core_logger import CoreLogger

from services.trade_router import TradeRouter
from services.trade_parser import TradeMessageParser
from entities.trade_details import TradeDetails


dash.register_page(__name__, path="/trades", name="Trades")


class TradesPage(BasePage):
    def render(self):
        return PageBody([
            PageHeader(f"{self.title}"),
            MainContent([
                html.H5("Paste Trade Signal"),
                dcc.Textarea(
                    id="signal-input",
                    style={"width": "100%", "height": "250px"},
                    placeholder="Paste AI signal here...",
                ),
                dbc.Row([
                    dbc.Col(dbc.Button("Parse Signal", id="parse-trade-btn", color="primary"), width="auto"),
                    dbc.Col(dbc.Button("Clear", id="clear-trade-btn", color="secondary", className="ms-2"), width="auto"),
                    dbc.Col(dbc.Button("Execute Trade", id="submit-trade-btn", color="success", className="ms-2", style={"display": "none"}), width="auto"),
                ], className="mt-2"),
                html.Div(id="parsed-trade-output", className="mt-3"),
                html.Div(id="trade-status", className="mt-3"),
                dcc.Store(id="parsed-trade-store"),
            ])
        ])


page = TradesPage(title="Trades")
layout = page.layout


@callback(
    Output("parsed-trade-output", "children", allow_duplicate=True),
    Output("parsed-trade-store", "data", allow_duplicate=True),
    Output("submit-trade-btn", "style", allow_duplicate=True),
    Input("parse-trade-btn", "n_clicks"),
    State("signal-input", "value"),
    prevent_initial_call=True
)
def parse_trade_signal(_, signal_input):
    if not signal_input:
        return dbc.Alert("Please paste a signal.", color="warning"), dash.no_update, {"display": "none"}

    try:
        trade_details = TradeMessageParser.parse(signal_input)
        preview = html.Ul([
            html.Li(f"Symbol: {trade_details.symbol}"),
            html.Li(f"Direction: {trade_details.direction}"),
            html.Li(f"Timeframe: {trade_details.timeframe}"),
            html.Li(f"Entry: {trade_details.entry}"),
            html.Li(f"Stop Loss: {trade_details.stop_loss}"),
            html.Li(f"Take Profit 1: {trade_details.take_profit_1}"),
            html.Li(f"Take Profit 2: {trade_details.take_profit_2 or '-'}"),
            html.Li(f"Take Profit 3: {trade_details.take_profit_3 or '-'}"),
            html.Li(f"AI Confidence: {trade_details.ai_confidence or '-'}%"),
        ])
        return preview, trade_details.__dict__, {"display": "inline-block"}

    except Exception as e:
        CoreLogger().error(f"Failed to parse signal: {e}")
        return dbc.Alert(f"Error parsing signal: {e}", color="danger"), dash.no_update, {"display": "none"}


@callback(
    Output("signal-input", "value", allow_duplicate=True),
    Output("parsed-trade-output", "children", allow_duplicate=True),
    Output("parsed-trade-store", "data", allow_duplicate=True),
    Output("submit-trade-btn", "style", allow_duplicate=True),
    Input("clear-trade-btn", "n_clicks"),
    prevent_initial_call=True
)
def clear_trade_ui(_):
    return "", None, None, {"display": "none"}


@callback(
    Output("trade-status", "children"),
    Input("submit-trade-btn", "n_clicks"),
    State("parsed-trade-store", "data"),
    prevent_initial_call=True
)
def execute_trade(_, trade_data):
    try:
        CoreLogger().info(f"Executing trade: {trade_data}")
        trade = TradeDetails(**{key.strip("_"): value for key, value in trade_data.items()})
        TradeRouter(trade).route_trade()
        return dbc.Alert("✅ Trade successfully routed!", color="success", dismissable=True)
    except Exception as e:
        CoreLogger().error(f"Execution failed: {e}")
        return dbc.Alert(f"Trade execution failed: {e}", color="danger", dismissable=True)
