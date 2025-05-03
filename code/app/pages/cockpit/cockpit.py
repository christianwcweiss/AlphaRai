from typing import Tuple, Any, Dict, Optional, List

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
from quant_core.enums.stagger_method import StaggerMethod
from quant_core.services.core_logger import CoreLogger
from quant_core.utils.trade_utils import get_stagger_levels, get_stagger_sizes
from services.trade_parser import TradeMessageParser
from services.trade_router import TradeRouter
from services.db.accounts import get_all_accounts, toggle_account_enabled

COCKPIT_PATH = "/"
dash.register_page(__name__, path=COCKPIT_PATH, name="Cockpit")

# IDS
TRADE_INPUT_TEXT_AREA_ID = "trade-input-text-area"
TRADE_OUTPUT_ID = "parsed-trade-output"
TRADE_ENTRY_SIMULATION_ID = "parsed-trade-entry-simulation-output"
TRADE_STORE_ID = "parsed-trade-store"


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
    account_cards = AlphaRow([render_account_card(account) for account in accounts])

    return account_cards


def trade_detail_row(label, value, emoji=""):
    return AlphaRow(
        [
            AlphaCol(html.Div(f"{emoji} {label}:"), width=4, style={"fontWeight": "bold", "textAlign": "right"}),
            AlphaCol(html.Div(value), width=8),
        ],
    )


class CockpitPage(BasePage):
    def _render_trading_section(self) -> html.Div:
        return html.Div(
            [
                SectionHeader("Paste Trade Signal").render(),
                AlphaRow(
                    [
                        AlphaCol(
                            dcc.Textarea(
                                id=TRADE_INPUT_TEXT_AREA_ID,
                                style={"width": "100%", "height": "400px"},
                                placeholder="Paste signal here...",
                            ),
                            xs=12,
                            sm=12,
                            md=12,
                            lg=6,
                            xl=6,
                        ),
                        AlphaCol(
                            [
                                AlphaButton(label="Parse Signal", button_id="parse-trade-btn").render(),
                                AlphaButton(label="Clear", button_id="clear-trade-btn").render(),
                                AlphaButton(label="Execute Trade", button_id="submit-trade-btn", style=HIDDEN).render(),
                            ],
                            xs=12,
                            sm=12,
                            md=12,
                            lg=6,
                            xl=6,
                        ),
                    ]
                ),
            ]
        )

    def render(self):
        return PageBody(
            [
                PageHeader(self._title).render(),
                MainContent(
                    [
                        self._render_trading_section(),
                        AlphaRow(
                            [
                                AlphaCol(html.Div(id=TRADE_OUTPUT_ID), lg=6),
                                AlphaCol(html.Div(id=TRADE_ENTRY_SIMULATION_ID), lg=6),
                            ]
                        ),
                        AlphaRow([AlphaCol(html.Div(id="trade-status"))]),
                        dcc.Store(id=TRADE_STORE_ID),
                        SectionHeader("Account Management").render(),
                        html.Div(render_account_cards(), id="account-toggle-container"),
                    ]
                ),
            ]
        )


layout = CockpitPage(title="Cockpit").layout


@callback(
    Output("account-toggle-container", "children"),
    Input({"type": "account-toggle", "index": dash.ALL}, "n_clicks"),
    State({"type": "account-toggle", "index": dash.ALL}, "id"),
)
def toggle_accounts(_, __) -> AlphaRow:
    if not ctx.triggered_id:
        return render_account_cards()

    triggered_uid = ctx.triggered_id["index"]
    toggle_account_enabled(triggered_uid)

    return render_account_cards()


@callback(
    Output(TRADE_OUTPUT_ID, "children", allow_duplicate=True),
    Output(TRADE_STORE_ID, "data", allow_duplicate=True),
    Output("submit-trade-btn", "style", allow_duplicate=True),
    Input("parse-trade-btn", "n_clicks"),
    State(TRADE_INPUT_TEXT_AREA_ID, "value"),
    prevent_initial_call=True,
)
def parse_trade_signal(_, signal_input: str):
    if not signal_input:
        return dbc.Alert("Please paste a signal...", color=colors.WARNING_COLOR), dash.no_update, HIDDEN

    try:
        trade_details = TradeMessageParser.parse(signal_input)
    except Exception as e:
        CoreLogger().error(f"Failed to parse signal: {e}")
        return dbc.Alert(f"Error parsing signal: {e}", color=colors.ERROR_COLOR), dash.no_update, HIDDEN

    preview = html.Div(
        [
            trade_detail_row("Symbol", trade_details.symbol, "🎯"),
            trade_detail_row("Direction", trade_details.direction.normalize().value.capitalize(), "↕️"),
            trade_detail_row("Timeframe", trade_details.timeframe, "⏱️"),
            trade_detail_row("Entry Price", trade_details.entry, "💰"),
            trade_detail_row("Stop Loss", trade_details.stop_loss, "🚩"),
            trade_detail_row("Take Profit 1", trade_details.take_profit_1, "🎯"),
            trade_detail_row("Take Profit 2", trade_details.take_profit_2 or "–", "🎯"),
            trade_detail_row("Take Profit 3", trade_details.take_profit_3 or "–", "🎯"),
            trade_detail_row("AI Confidence", f"{trade_details.ai_confidence or '–'}%", "🤖"),
        ],
        style={
            "padding": "1rem",
            "fontSize": "1.05rem",
            "backgroundColor": "#f9f9fa",
            "borderRadius": "12px",
            "boxShadow": "0 2px 6px rgba(0,0,0,0.05)",
        },
    )

    return preview, trade_details.to_dict(), AlphaButton.DEFAULT_STYLE


@callback(
    Output(TRADE_INPUT_TEXT_AREA_ID, "value", allow_duplicate=True),
    Output(TRADE_OUTPUT_ID, "children", allow_duplicate=True),
    Output(TRADE_STORE_ID, "data", allow_duplicate=True),
    Output("submit-trade-btn", "style", allow_duplicate=True),
    Input("clear-trade-btn", "n_clicks"),
    prevent_initial_call=True,
)
def clear_trade_ui(_) -> Tuple[str, Optional[List[Component]], Optional[Dict[str, Any]], Dict[str, Any]]:
    return "", None, None, HIDDEN


@callback(
    Output("trade-status", "children"),
    Input("submit-trade-btn", "n_clicks"),
    State(TRADE_STORE_ID, "data"),
    prevent_initial_call=True,
)
def execute_trade(_, trade_data: Dict[str, Any]) -> dbc.Alert:
    try:
        CoreLogger().info(f"Routing Trade: {trade_data}")
        trade = TradeDetails(**trade_data)
        TradeRouter(trade).route_trade()
        return dbc.Alert("✅ Trade successfully routed!", color=colors.SUCCESS_COLOR, dismissable=True)
    except Exception as e:
        CoreLogger().error(f"Execution failed: {e}")
        return dbc.Alert(f"Trade execution failed: {e}", color=colors.ERROR_COLOR, dismissable=True)
