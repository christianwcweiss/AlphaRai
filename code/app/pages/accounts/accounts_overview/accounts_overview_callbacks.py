from typing import Tuple, Optional

import dash
import pandas as pd
from dash import Input, Output, State, ctx, callback, ALL, html
from dash.exceptions import PreventUpdate

from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.molecules.cards.settings.account_card import AccountSettingsCard
from models.main.account import Account
from quant_core.enums.platform import Platform
from quant_core.metrics.account_balance_over_time.balance_over_time import AccountBalanceOverTime
from quant_core.utils.text_utils import generate_uid
from services.db.cache.trade_history import get_all_trades_df
from services.db.main.account import (
    upsert_account,
    delete_account,
    get_all_accounts,
)


def render_account_card(account: Account, history_data_frame: pd.DataFrame) -> html.Div:
    """Render the account card with the given account and relative DataFrame."""
    data_frame = (
        history_data_frame[history_data_frame["account_id"] == account.uid] if not history_data_frame.empty else None
    )

    return AccountSettingsCard(account, data_frame).render()


def reload_mt5_accounts():
    """Reload the MT5 accounts and their trades."""
    accounts = sorted(get_all_accounts(), key=lambda x: x.friendly_name)
    trades_df = get_all_trades_df()

    balance_df = AccountBalanceOverTime().calculate(
        data_frame=trades_df,
    )

    return AlphaRow(
        [AlphaCol(render_account_card(account, balance_df), xs=12, sm=6, md=4, lg=3, xl=3) for account in accounts]
    )


@callback(
    Output("add-account-modal", "is_open"),
    Input("open-add-mt5-btn", "n_clicks"),
    Input("close-add-account", "n_clicks"),
    Input("confirm-add-account", "n_clicks"),
    State("add-account-modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_add_modal(
    _open_add_account_btn_clicks: int, _close_add_account_clicks: int, _confirm_add_account_clicks: int, is_open: bool
) -> bool:
    """Toggle the add account modal."""
    triggered = ctx.triggered_id
    if triggered == "open-add-mt5-btn":
        return True
    if triggered in ["close-add-account", "confirm-add-account"]:
        return False

    return is_open


@callback(
    Output("mt5-rows", "children", allow_duplicate=True),
    Input("confirm-add-account", "n_clicks"),
    State("input-account-name", "value"),
    State("input-account-secret", "value"),
    prevent_initial_call=True,
)
def save_new_account(_, label: str, secret: str) -> AlphaRow:
    """Save the new MT5 account."""
    if not label or not secret:
        raise PreventUpdate

    upsert_account(Platform.METATRADER.value, label, secret, generate_uid(length=8))
    return reload_mt5_accounts()


@callback(
    Output("mt5-rows", "children", allow_duplicate=True),
    Input("page-init", "children"),
    prevent_initial_call="initial_duplicate",
)
def load_mt5_credentials_on_page_load(_) -> AlphaRow:
    """Load the MT5 accounts on page load."""
    return reload_mt5_accounts()


@callback(
    Output("mt5-rows", "children", allow_duplicate=True),
    Output("delete-confirm-modal", "is_open", allow_duplicate=True),
    Output("pending-delete-uid", "data", allow_duplicate=True),
    [
        Input({"type": "initiate-delete", "index": ALL}, "n_clicks"),
        Input("cancel-delete-btn", "n_clicks"),
        Input("confirm-delete-btn", "n_clicks"),
    ],
    [
        State("pending-delete-uid", "data"),
        State({"type": "initiate-delete", "index": ALL}, "id"),
    ],
    prevent_initial_call=True,
)
def manage_delete(_, __, ___, pending_uid, ____) -> Tuple[
    dash.no_update,
    bool,
    Optional[str],
]:
    """Manage the delete confirmation modal and account deletion."""
    triggered = ctx.triggered_id

    if triggered == "cancel-delete-btn":
        return dash.no_update, False, dash.no_update

    if triggered == "confirm-delete-btn":
        if pending_uid:
            delete_account(Platform.METATRADER.value, pending_uid)
            return reload_mt5_accounts(), False, None

        raise PreventUpdate

    if isinstance(triggered, dict) and triggered.get("type") == "initiate-delete":
        return dash.no_update, True, triggered["index"]

    raise PreventUpdate
