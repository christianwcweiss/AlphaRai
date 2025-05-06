import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, ctx, callback
from dash.development.base_component import Component

from components.atoms.buttons.button import AlphaButton
from components.atoms.content import MainContent
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.atoms.text.page import PageHeader
from components.atoms.text.section import SectionHeader
from components.frame.body import PageBody
from constants import colors
from constants.style import HIDDEN
from entities.trade_details import TradeDetails
from models.account import Account
from pages.base_page import BasePage
from quant_core.services.core_logger import CoreLogger
from services.db.account import get_all_accounts, toggle_account_enabled
from services.trade_parser import TradeMessageParser
from services.trade_router import TradeRouter

COCKPIT_PATH = "/"
dash.register_page(__name__, path=COCKPIT_PATH, name="Cockpit")

TRADE_INPUT_TEXT_AREA_ID = "trade-input-text-area"
TRADE_OUTPUT_ID = "parsed-trade-output"
TRADE_STORE_ID = "parsed-trade-store"
NEW_TRADE_MODAL_ID = "new-trade-modal"
OPEN_TRADE_MODAL_BTN_ID = "open-trade-modal-btn"


def render_account_card(account: Account) -> AlphaCol:
    return AlphaCol(
        AlphaButton(
            label=f"{account.platform} {account.friendly_name}",
            button_id={"type": "account-toggle", "index": account.uid},
            style={"backgroundColor": colors.PRIMARY_COLOR if account.enabled else colors.ERROR_COLOR},
        ).render(),
        xs=12,
        sm=6,
        md=6,
        lg=4,
        xl=4,
    )


def render_account_cards() -> AlphaRow:
    accounts = get_all_accounts()
    return AlphaRow([render_account_card(account) for account in accounts])


def trade_detail_row(label, value, emoji=""):
    return AlphaRow([
        AlphaCol(html.Div(f"{emoji} {label}:", className="fw-bold text-end"), width=4),
        AlphaCol(html.Div(value), width=8),
    ])


def trade_detail_modal() -> dbc.Modal:
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("New Trade")),
        dbc.ModalBody([
            dcc.Textarea(
                id=TRADE_INPUT_TEXT_AREA_ID,
                style={"width": "100%", "height": "200px"},
                placeholder="Paste signal here...",
            ),
            html.Br(),
            AlphaButton("Parse Signal", "parse-trade-btn").render(),
            html.Br(), html.Br(),
            html.Div(id=TRADE_OUTPUT_ID),
            html.Br(),
            AlphaButton("Execute Trade", "submit-trade-btn", style=HIDDEN).render(),
        ]),
        dbc.ModalFooter([
            AlphaButton("Close", "close-trade-modal-btn").render()
        ])
    ],
        id=NEW_TRADE_MODAL_ID,
        is_open=False,
        size="lg",
        backdrop="static",
        keyboard=False
    )


class CockpitPage(BasePage):
    def render(self):
        return PageBody([
            PageHeader(self._title).render(),
            MainContent([
                AlphaButton("➕ New Trade", OPEN_TRADE_MODAL_BTN_ID).render(),
                trade_detail_modal(),
                AlphaRow([AlphaCol(html.Div(id="trade-status"))]),
                dcc.Store(id=TRADE_STORE_ID),
                SectionHeader("Account Management").render(),
                html.Div(render_account_cards(), id="account-toggle-container"),
            ])
        ])


layout = CockpitPage("Cockpit").layout


@callback(
    Output("account-toggle-container", "children"),
    Input({"type": "account-toggle", "index": dash.ALL}, "n_clicks"),
    State({"type": "account-toggle", "index": dash.ALL}, "id"),
)
def toggle_accounts(_, __):
    if not ctx.triggered_id:
        return render_account_cards()
    toggle_account_enabled(ctx.triggered_id["index"])
    return render_account_cards()


@callback(
    Output(TRADE_OUTPUT_ID, "children", allow_duplicate=True),
    Output(TRADE_STORE_ID, "data", allow_duplicate=True),
    Output("submit-trade-btn", "style", allow_duplicate=True),
    Input("parse-trade-btn", "n_clicks"),
    State(TRADE_INPUT_TEXT_AREA_ID, "value"),
    prevent_initial_call=True,
)
def parse_trade_signal(_, signal_input):
    if not signal_input:
        return dbc.Alert("Please paste a signal...", color=colors.WARNING_COLOR), dash.no_update, HIDDEN
    try:
        trade_details = TradeMessageParser.parse(signal_input)
    except Exception as e:
        CoreLogger().error(f"Failed to parse signal: {e}")
        return dbc.Alert(f"Error parsing signal: {e}", color=colors.ERROR_COLOR), dash.no_update, HIDDEN

    preview = html.Div([
        trade_detail_row("Symbol", trade_details.symbol, "🎯"),
        trade_detail_row("Direction", trade_details.direction.normalize().value.capitalize(), "↕️"),
        trade_detail_row("Timeframe", trade_details.timeframe, "⏱️"),
        trade_detail_row("Entry Price", trade_details.entry, "💰"),
        trade_detail_row("Stop Loss", trade_details.stop_loss, "🚩"),
        trade_detail_row("Take Profit 1", trade_details.take_profit_1, "🎯"),
        trade_detail_row("Take Profit 2", trade_details.take_profit_2 or "–", "🎯"),
        trade_detail_row("Take Profit 3", trade_details.take_profit_3 or "–", "🎯"),
        trade_detail_row("AI Confidence", f"{trade_details.ai_confidence or '–'}%", "🤖"),
    ], style={
        "padding": "1rem",
        "fontSize": "1.05rem",
        "backgroundColor": "#f9f9fa",
        "borderRadius": "12px",
        "boxShadow": "0 2px 6px rgba(0,0,0,0.05)",
    })

    return preview, trade_details.to_dict(), AlphaButton.DEFAULT_STYLE


@callback(
    Output(TRADE_INPUT_TEXT_AREA_ID, "value", allow_duplicate=True),
    Output(TRADE_OUTPUT_ID, "children", allow_duplicate=True),
    Output(TRADE_STORE_ID, "data", allow_duplicate=True),
    Output("submit-trade-btn", "style", allow_duplicate=True),
    Input("close-trade-modal-btn", "n_clicks"),
    prevent_initial_call=True,
)
def clear_trade_ui(_):
    return "", None, None, HIDDEN


@callback(
    Output("trade-status", "children"),
    Input("submit-trade-btn", "n_clicks"),
    State(TRADE_STORE_ID, "data"),
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


@callback(
    Output(NEW_TRADE_MODAL_ID, "is_open"),
    [
        Input(OPEN_TRADE_MODAL_BTN_ID, "n_clicks"),
        Input("close-trade-modal-btn", "n_clicks"),
    ],
    State(NEW_TRADE_MODAL_ID, "is_open"),
    prevent_initial_call=True,
)
def toggle_trade_modal(_, __, is_open):
    return not is_open
