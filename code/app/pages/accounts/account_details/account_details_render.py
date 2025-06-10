from typing import List

import dash_bootstrap_components as dbc
from components.atoms.buttons.general.button import AlphaButton, AlphaButtonColor
from components.atoms.layout.layout import AlphaCol, AlphaRow
from components.molecules.cards.accounts.symbol_card import AccountConfigCard
from dash import dcc, html
from models.main.account_config import AccountConfig
from pages.accounts.account_details.account_details_constants import (
    EDIT_ACCOUNT_CONFIG_BUTTON_ID,
    EDIT_ASSET_TYPE_ID,
    EDIT_CONFIG_ID,
    EDIT_ENABLED_ID,
    EDIT_ENTRY_OFFSET_ID,
    EDIT_MODAL_BODY_ID,
    EDIT_MODAL_BUTTON_CANCEL_ID,
    EDIT_MODAL_BUTTON_SAVE_ID,
    EDIT_MODAL_CANCEL_BUTTON_LABEL,
    EDIT_MODAL_ID,
    EDIT_MODAL_SAVE_BUTTON_LABEL,
    EDIT_MODE_ID,
    EDIT_N_STAGGERS_ID,
    EDIT_PLATFORM_ASSET_ID,
    EDIT_RISK_ID,
    EDIT_SIGNAL_ASSET_ID,
    EDIT_STAGGER_METHOD_ID,
    SYNC_MT5_BUTTON_ID,
    SYNC_MT5_BUTTON_LABEL,
)
from quant_core.enums.asset_type import AssetType
from quant_core.enums.stagger_method import StaggerMethod
from quant_core.enums.trade_direction import EnabledTradeDirection
from quant_core.enums.trade_mode import TradeMode


def render_account_details_row() -> html.Div:
    """Render the account details row."""
    return html.Div(
        [
            html.H5("Account Details"),
            html.P("This section contains details about the selected account."),
        ]
    )


def render_activated_symbol_stats() -> html.Div:
    """Render the activated symbol stats."""
    return html.Div(
        [
            html.H5("Activated Symbols"),
            html.P("This section shows the symbols that are currently enabled for trading."),
        ]
    )


def render_edit_modal() -> dbc.Modal:
    """Render the edit modal for account configurations."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Edit Configuration")),
            dbc.ModalBody(
                id=EDIT_MODAL_BODY_ID,
                children=[
                    dcc.Dropdown(id=EDIT_SIGNAL_ASSET_ID),
                    dcc.Dropdown(id=EDIT_PLATFORM_ASSET_ID),
                    dcc.Dropdown(id=EDIT_STAGGER_METHOD_ID),
                    dcc.Dropdown(id=EDIT_ENTRY_OFFSET_ID),
                    dcc.Dropdown(id=EDIT_N_STAGGERS_ID),
                    dcc.Dropdown(id=EDIT_RISK_ID),
                    dcc.Dropdown(id=EDIT_MODE_ID),
                    dcc.Dropdown(id=EDIT_ASSET_TYPE_ID),
                    dcc.Dropdown(id=EDIT_ENABLED_ID),
                    dcc.Store(id=EDIT_CONFIG_ID),
                ],
            ),
            dbc.ModalFooter(
                children=[
                    AlphaCol(
                        AlphaButton(
                            label=EDIT_MODAL_SAVE_BUTTON_LABEL,
                            button_id=EDIT_MODAL_BUTTON_SAVE_ID,
                            button_color=AlphaButtonColor.CONFIRM,
                        ).render(),
                    ),
                    AlphaCol(
                        AlphaButton(
                            label=EDIT_MODAL_CANCEL_BUTTON_LABEL,
                            button_id=EDIT_MODAL_BUTTON_CANCEL_ID,
                            button_color=AlphaButtonColor.CANCEL,
                        ).render(),
                    ),
                ]
            ),
        ],
        id=EDIT_MODAL_ID,
        is_open=False,
        size="lg",
        backdrop="static",
    )


def render_account_config_card(account_config: AccountConfig) -> html.Div:
    """Render the symbol cards for enabled and disabled symbols."""
    return AccountConfigCard(edit_button_id=EDIT_ACCOUNT_CONFIG_BUTTON_ID, account_config=account_config).render()


def render_account_config_cards(account_configs: List[AccountConfig]) -> html.Div:
    """Render the symbol rows for enabled and disabled symbols."""

    return html.Div(
        children=[
            AlphaRow(
                children=[
                    AlphaCol(
                        render_account_config_card(
                            account_config=account_config,
                        ),
                        xs=12,
                        sm=4,
                        md=3,
                        lg=3,
                        xl=3,
                    )
                    for account_config in sorted(account_configs, key=lambda x: x.platform_asset_id)
                    if account_config.enabled_trade_direction
                    in (EnabledTradeDirection.LONG, EnabledTradeDirection.SHORT, EnabledTradeDirection.BOTH)
                ]
            ),
            AlphaRow(
                children=[
                    AlphaCol(
                        render_account_config_card(
                            account_config=account_config,
                        ),
                        xs=12,
                        sm=6,
                        md=4,
                        lg=3,
                        xl=3,
                    )
                    for account_config in sorted(account_configs, key=lambda x: x.platform_asset_id)
                    if account_config.enabled_trade_direction is EnabledTradeDirection.DISABLED
                ]
            ),
        ]
    )


def render_edit_modal_body(config: AccountConfig) -> html.Div:
    """Render the body of the edit modal for an account configuration."""
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Signal Asset ID"),
                            dbc.Input(id=EDIT_SIGNAL_ASSET_ID, type="text", value=config.signal_asset_id),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Platform Asset ID"),
                            dbc.Input(id=EDIT_PLATFORM_ASSET_ID, type="text", value=config.platform_asset_id),
                        ],
                        md=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Entry Stagger Method"),
                            dcc.Dropdown(
                                id=EDIT_STAGGER_METHOD_ID,
                                options=[{"label": m.name, "value": m} for m in list(StaggerMethod)],
                                value=config.entry_stagger_method,
                                clearable=False,
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Number of Staggers"),
                            dbc.Input(id=EDIT_N_STAGGERS_ID, type="number", min=1, value=config.n_staggers),
                        ],
                        md=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Risk %"),
                            dbc.Input(id=EDIT_RISK_ID, type="number", step=0.1, min=0.1, value=config.risk_percent),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Mode"),
                            dcc.Dropdown(
                                id=EDIT_MODE_ID,
                                options=[{"label": m.name, "value": m} for m in TradeMode],
                                value=config.mode if config.mode else TradeMode.DEFAULT.name,
                                clearable=False,
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Asset Type"),
                            dcc.Dropdown(
                                id=EDIT_ASSET_TYPE_ID,
                                options=[{"label": a.name, "value": a.name} for a in AssetType],
                                value=config.asset_type.name if config.asset_type else None,
                                clearable=True,
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Enabled"),
                            dcc.Dropdown(
                                id=EDIT_ENABLED_ID,
                                options=[
                                    {"label": enabled_option.name, "value": enabled_option.name}
                                    for enabled_option in EnabledTradeDirection
                                ],
                                value=config.enabled_trade_direction.name if config.enabled_trade_direction else None,
                                clearable=True,
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="mb-3",
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Lot Size"),
                            dbc.Input(value=config.lot_size, disabled=True),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Decimals"),
                            dbc.Input(value=config.decimal_points, disabled=True),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Account ID"),
                            dbc.Input(value=config.account_id, disabled=True),
                        ],
                        md=4,
                    ),
                ]
            ),
            dcc.Store(id=EDIT_CONFIG_ID, data=config.platform_asset_id),
        ]
    )


def render_symbol_sync_button() -> html.Div:
    """Render the symbol sync button."""
    return AlphaButton(
        label=SYNC_MT5_BUTTON_LABEL, button_id=SYNC_MT5_BUTTON_ID, button_color=AlphaButtonColor.PRIMARY
    ).render()
