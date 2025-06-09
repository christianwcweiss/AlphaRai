from typing import List, Tuple

import dash
from components.atoms.text.page import PageHeader
from dash import ALL, Input, Output, State, callback, ctx, html
from pages.accounts.account_details.account_details_constants import (
    CARD_CONTAINER,
    DYNAMIC_HEADER,
    EDIT_ACCOUNT_CONFIG_BUTTON_ID,
    EDIT_ASSET_TYPE_ID,
    EDIT_CONFIG_ID,
    EDIT_ENABLED_ID,
    EDIT_MODAL_BODY_ID,
    EDIT_MODAL_BUTTON_CANCEL_ID,
    EDIT_MODAL_BUTTON_SAVE_ID,
    EDIT_MODAL_ID,
    EDIT_MODE_ID,
    EDIT_N_STAGGERS_ID,
    EDIT_PLATFORM_ASSET_ID,
    EDIT_RISK_ID,
    EDIT_SIGNAL_ASSET_ID,
    EDIT_STAGGER_METHOD_ID,
    SETTINGS_UID,
    SETTINGS_URL,
    SYNC_MT5_BUTTON_ID,
)
from pages.accounts.account_details.account_details_render import render_account_config_cards, render_edit_modal_body
from services.db.main.account import AccountService
from services.db.main.account_config import AccountConfigService


@callback(
    Output(SETTINGS_UID, "children"),
    Output(DYNAMIC_HEADER, "children"),
    Input(SETTINGS_URL, "pathname"),
    prevent_initial_call=True,
)
def extract_uid_from_url(pathname: str) -> Tuple[str, html.Div]:
    """Extract the UID from the URL and display the dynamic header."""
    uid = pathname.split("/")[-1]
    account = AccountService().get_account_by_uid(uid=uid)
    if not account:
        raise dash.exceptions.PreventUpdate

    return uid, PageHeader(f'Account "{account.friendly_name}"').render()


@callback(
    Output(CARD_CONTAINER, "children"),
    Input(SETTINGS_UID, "children"),
    prevent_initial_call=True,
)
def render_config_cards(uid: str) -> html.Div:
    """Render the tables for enabled and disabled configurations."""
    account_configs = AccountConfigService().get_configs_by_account(uid)

    return render_account_config_cards(account_configs)


@callback(
    Output(CARD_CONTAINER, "children", allow_duplicate=True),
    Input(SYNC_MT5_BUTTON_ID, "n_clicks"),
    State(SETTINGS_UID, "children"),
    prevent_initial_call=True,
)
def sync_symbols_callback(_sync_button_clicks: int, uid: str) -> html.Div:
    """Sync symbols with MT5."""
    account = AccountService().get_account_by_uid(uid)
    if not account:
        raise dash.exceptions.PreventUpdate

    AccountConfigService().sync_with_mt5(account_uid=uid, secret_id=account.secret_name)

    return render_config_cards(uid)


@callback(
    Output(EDIT_MODAL_ID, "is_open"),
    Output(EDIT_MODAL_BODY_ID, "children"),
    [Input({"type": EDIT_ACCOUNT_CONFIG_BUTTON_ID, "index": ALL}, "n_clicks")],
    State(EDIT_MODAL_ID, "is_open"),
    State(SETTINGS_UID, "children"),
    prevent_initial_call=True,
)
def open_edit_modal(n_clicks: List[int], _is_open: bool, uid: str) -> Tuple[bool, html.Div]:
    """Open the edit modal for the account configuration."""
    triggered_symbol = dash.ctx.triggered_id["index"]

    if all(click is None or click == 0 for click in n_clicks) or not triggered_symbol:
        raise dash.exceptions.PreventUpdate

    config = AccountConfigService().get_config(account_uid=uid, platform_asset_id=triggered_symbol)
    if not config:
        raise dash.exceptions.PreventUpdate

    return True, render_edit_modal_body(config=config)


@callback(
    Output(EDIT_MODAL_ID, "is_open", allow_duplicate=True),
    Output(CARD_CONTAINER, "children", allow_duplicate=True),
    Input(EDIT_MODAL_BUTTON_SAVE_ID, "n_clicks"),
    Input(EDIT_MODAL_BUTTON_CANCEL_ID, "n_clicks"),
    State(EDIT_SIGNAL_ASSET_ID, "value"),
    State(EDIT_PLATFORM_ASSET_ID, "value"),
    State(EDIT_STAGGER_METHOD_ID, "value"),
    State(EDIT_N_STAGGERS_ID, "value"),
    State(EDIT_RISK_ID, "value"),
    State(EDIT_MODE_ID, "value"),
    State(EDIT_ASSET_TYPE_ID, "value"),
    State(EDIT_ENABLED_ID, "value"),
    State(EDIT_CONFIG_ID, "data"),
    State(SETTINGS_UID, "children"),
    prevent_initial_call=True,
)
def save_config(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    _save_clicks: int,
    _cancel_clicks: int,
    signal_asset_id: str,
    platform_asset_id: str,
    method: str,
    n_staggers: int,
    risk: float,
    mode: str,
    asset_type: str,
    enabled: bool,
    config_id: str,
    uid: str,
) -> Tuple[bool, html.Div]:
    """Save or cancel edits to account config. Close modal and refresh cards."""
    if ctx.triggered_id == EDIT_MODAL_BUTTON_CANCEL_ID:
        return False, dash.no_update

    if ctx.triggered_id == EDIT_MODAL_BUTTON_SAVE_ID:
        AccountConfigService().upsert_configs(
            account_uid=uid,
            configs={
                "id": config_id,
                "signal_asset_id": signal_asset_id,
                "platform_asset_id": platform_asset_id,
                "entry_stagger_method": method,
                "n_staggers": n_staggers,
                "risk_percent": risk,
                "mode": mode,
                "asset_type": asset_type,
                "enabled": enabled,
            },
        )
        updated_cards = render_account_config_cards(AccountConfigService().get_configs_by_account(uid))

        return False, updated_cards

    raise dash.exceptions.PreventUpdate
