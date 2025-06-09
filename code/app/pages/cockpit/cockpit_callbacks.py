from typing import Any, Dict, List, Optional, Union

import dash
from components.atoms.layout.layout import AlphaRow
from dash import Input, Output, State, callback, ctx, html
from pages.cockpit.cockpit_constants import ACCOUNT_TOGGLE_ID, START_BOT_BTN_ID, STOP_BOT_BTN_ID
from pages.cockpit.cockpit_render import render_account_management_row, render_account_cards, render_bot_controls_row
from services.db.main.account import AccountService
from services.relay_bot import DiscordRelayBot

bot_instance = DiscordRelayBot()


@callback(
    Output("account-toggle-container", "children"),
    Input(START_BOT_BTN_ID, "n_clicks"),
    Input(STOP_BOT_BTN_ID, "n_clicks"),
    Input({"type": ACCOUNT_TOGGLE_ID, "index": dash.ALL}, "n_clicks"),
    State({"type": ACCOUNT_TOGGLE_ID, "index": dash.ALL}, "id"),
    prevent_initial_call=True,
)
def control_bot_and_toggle_accounts(
    _start_bot_clicks: int,
    _stop_bot_clicks: int,
    _account_toggle_clicks: List[int],
    _account_toggle_ids: List[Optional[Union[Dict[str, Any], str, int]]],
) -> html.Div:
    """Control the Discord bot and toggle account states based on user interactions."""
    triggered = ctx.triggered_id

    if triggered == START_BOT_BTN_ID:
        bot_instance.run()

    elif triggered == STOP_BOT_BTN_ID:
        bot_instance.stop()

    elif isinstance(triggered, dict) and triggered.get("type") == ACCOUNT_TOGGLE_ID:
        AccountService().toggle_account_enabled(triggered["index"])

    return render_account_cards()


@callback(
    Output("bot-controls-container", "children"),
    Input("bot-status-interval", "n_intervals"),
)
def update_bot_status(_n_intervals: int) -> html.Div:
    """Update the bot controls based on the current status of the Discord bot."""
    return render_bot_controls_row(bot_instance.is_running())
