from typing import Any, Dict, List, Optional, Union

import dash
from dash import Input, Output, State, callback, ctx, html
from pages.cockpit.cockpit_constants import (
    ACCOUNT_TOGGLE_ID,
    BOT_CONTROLS_CONTAINER,
    BOT_STATUS_INTERVAL_ID,
    START_BOT_BTN_ID,
    STOP_BOT_BTN_ID,
)
from pages.cockpit.cockpit_render import render_account_cards, render_bot_controls_row
from services.db.main.account import AccountService
from services.relay_bot import DiscordRelayBot

bot_instance = DiscordRelayBot()


@callback(
    Output("account-toggle-container", "children"),
    Input({"type": ACCOUNT_TOGGLE_ID, "index": dash.ALL}, "n_clicks"),
    State({"type": ACCOUNT_TOGGLE_ID, "index": dash.ALL}, "id"),
)
def control_bot_and_toggle_accounts(
    _account_toggle_clicks: List[int],
    _account_toggle_ids: List[Optional[Union[Dict[str, Any], str, int]]],
) -> html.Div:
    """Control the Discord bot and toggle account states based on user interactions."""
    triggered = ctx.triggered_id

    if isinstance(triggered, dict) and triggered.get("type") == ACCOUNT_TOGGLE_ID:
        AccountService().toggle_account_enabled(triggered["index"])
    else:
        return dash.no_update

    return render_account_cards()


@callback(
    Output(BOT_CONTROLS_CONTAINER, "children"),
    Input(START_BOT_BTN_ID, "n_clicks"),
    Input(STOP_BOT_BTN_ID, "n_clicks"),
    Input(BOT_STATUS_INTERVAL_ID, "n_intervals"),
)
def toggle_bot_on(_start_btn_clicks: int, _stop_btn_clicks: int, _nth_interval: int) -> html.Div:
    """Toggle the Discord bot on or off based on button clicks."""
    triggered = ctx.triggered_id

    if triggered == START_BOT_BTN_ID:
        bot_instance.run()
    elif triggered == STOP_BOT_BTN_ID:
        bot_instance.stop()

    return render_bot_controls_row(bot_instance.is_running())
