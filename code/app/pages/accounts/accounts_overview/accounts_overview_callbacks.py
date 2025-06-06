from typing import Any, List, Optional, Tuple

import dash
from components.atoms.layout.layout import AlphaRow
from dash import ALL, Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate
from pages.accounts.accounts_overview.accounts_overview_constants import (
    ADD_ACCOUNT_CANCEL_BUTTON_ID,
    ADD_ACCOUNT_CONFIRM_BUTTON_ID,
    ADD_ACCOUNT_MODAL_ID,
    CONTENT_ROWS,
    DELETE_ACCOUNT_MODAL_CANCEL_BUTTON_ID,
    DELETE_ACCOUNT_MODAL_CONFIRM_BUTTON_ID,
    DELETE_ACCOUNT_MODAL_ID,
    INPUT_ACCOUNT_NAME_ID,
    INPUT_ACCOUNT_SECRET_ID,
    INPUT_PLATFORM_ID,
    INPUT_PROP_FIRM,
    OPEN_ADD_ACCOUNT_MODAL_ID,
    PAGE_INIT,
    PENDING_DELETE_UID_ID,
)
from pages.accounts.accounts_overview.accounts_overview_render import render_all_accounts
from quant_core.enums.platform import Platform
from quant_core.enums.prop_firm import PropFirm
from quant_core.services.core_logger import CoreLogger
from quant_core.utils.text_utils import generate_uid
from services.db.main.account import AccountService


@callback(
    Output(ADD_ACCOUNT_MODAL_ID, "is_open"),
    Input(OPEN_ADD_ACCOUNT_MODAL_ID, "n_clicks"),
    Input(ADD_ACCOUNT_CONFIRM_BUTTON_ID, "n_clicks"),
    Input(ADD_ACCOUNT_CANCEL_BUTTON_ID, "n_clicks"),
    State(ADD_ACCOUNT_MODAL_ID, "is_open"),
    prevent_initial_call=True,
)
def toggle_add_modal(
    _open_add_account_btn_clicks: int, _confirm_add_account_clicks: int, _cancel_add_account_clicks: int, is_open: bool
) -> bool:
    """Toggle the add account modal."""
    triggered = ctx.triggered_id
    if triggered == OPEN_ADD_ACCOUNT_MODAL_ID:
        return True
    if triggered in [ADD_ACCOUNT_CONFIRM_BUTTON_ID, ADD_ACCOUNT_CANCEL_BUTTON_ID]:
        return False

    return is_open


@callback(
    Output(CONTENT_ROWS, "children", allow_duplicate=True),
    Input(ADD_ACCOUNT_CONFIRM_BUTTON_ID, "n_clicks"),
    Input(ADD_ACCOUNT_CANCEL_BUTTON_ID, "n_clicks"),
    State(INPUT_ACCOUNT_NAME_ID, "value"),
    State(INPUT_ACCOUNT_SECRET_ID, "value"),
    State(INPUT_PLATFORM_ID, "value"),
    State(INPUT_PROP_FIRM, "value"),
    prevent_initial_call=True,
)
def save_new_account(
    _confirm_clicks: int, _cancel_clicks: int, account_name: str, account_secret: str, platform: str, prop_firm: str
) -> AlphaRow:
    """Save the new account."""
    if not account_name or not account_secret or not platform or not prop_firm:
        raise PreventUpdate

    if ctx.triggered_id == ADD_ACCOUNT_CANCEL_BUTTON_ID:
        return render_all_accounts()

    AccountService().upsert_account(
        friendly_name=account_name,
        secret_name=account_secret,
        platform=Platform(platform),
        prop_firm=PropFirm(prop_firm),
        uid=generate_uid(),
    )

    return render_all_accounts()


@callback(
    Output(CONTENT_ROWS, "children", allow_duplicate=True),
    Input(PAGE_INIT, "children"),
    prevent_initial_call="initial_duplicate",
)
def load_mt5_credentials_on_page_load(_: Any) -> AlphaRow:
    """Load the MT5 accounts on page load."""
    return render_all_accounts()


@callback(
    Output(CONTENT_ROWS, "children", allow_duplicate=True),
    Output(DELETE_ACCOUNT_MODAL_ID, "is_open", allow_duplicate=True),
    Output(PENDING_DELETE_UID_ID, "data", allow_duplicate=True),
    [
        Input({"type": "initiate-delete", "index": ALL}, "n_clicks"),
        Input(DELETE_ACCOUNT_MODAL_CANCEL_BUTTON_ID, "n_clicks"),
        Input(DELETE_ACCOUNT_MODAL_CONFIRM_BUTTON_ID, "n_clicks"),
    ],
    [
        State({"type": "initiate-delete", "index": ALL}, "id"),
    ],
    prevent_initial_call=True,
)
def manage_delete(
    initial_delete_clicks: List[int],
    _cancel_delete_button_clicks: int,
    _confirm_delete_button_clicks: int,
    pending_uid_state: Any,
) -> Tuple[
    dash.no_update,
    bool,
    Optional[str],
]:
    """Manage the delete confirmation modal and account deletion."""
    triggered = ctx.triggered_id

    CoreLogger().info(triggered)

    if triggered == DELETE_ACCOUNT_MODAL_CANCEL_BUTTON_ID:
        return dash.no_update, False, dash.no_update

    if triggered == DELETE_ACCOUNT_MODAL_CONFIRM_BUTTON_ID:
        if pending_uid_state:
            uid = next(
                iter(ids.get("index") for clicks, ids in zip(initial_delete_clicks, pending_uid_state) if clicks), None
            )
            account = AccountService().get_account_by_uid(uid)
            AccountService().delete_account(account.uid)

            return render_all_accounts(), False, None

        raise PreventUpdate

    if (
        any(clicks > 0 for clicks in initial_delete_clicks)
        and isinstance(triggered, dict)
        and triggered.get("type") == "initiate-delete"
    ):
        pending_uid = triggered.get("index")
        if pending_uid:
            return dash.no_update, True, pending_uid

    raise PreventUpdate
