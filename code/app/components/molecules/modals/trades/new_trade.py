from typing import Any, Dict, List, Optional, Tuple

import dash_bootstrap_components as dbc
from components.atoms.buttons.general.button import AlphaButton
from components.atoms.card.card import AlphaCard, AlphaCardBody, AlphaCardHeader
from components.atoms.divider.divider import Divider
from components.atoms.layout.layout import AlphaCol, AlphaRow
from components.molecules.molecule import Molecule
from constants import colors
from constants.style import HIDDEN
from dash import Input, Output, State, callback, dash, dcc, html
from dash_bootstrap_components import Alert
from entities.trade_details import TradeDetails
from models.main.account import Account
from models.main.account_config import AccountConfig
from quant_core.clients.mt5.mt5_client import Mt5Client
from quant_core.enums.stagger_method import StaggerMethod
from quant_core.services.core_logger import CoreLogger
from quant_core.utils.trade_utils import (
    calculate_position_size,
    calculate_risk_reward,
    calculate_weighted_risk_reward,
    get_stagger_levels,
)
from services.db.main.account import AccountService
from services.db.main.account_config import AccountConfigService
from services.trade_parser import TradeMessageParser
from services.trade_router import TradeRouter


def _render_trade_input_text_area() -> html.Div:
    """Render the trade input text area."""
    return html.Div(
        [
            dcc.Textarea(
                id="trade-input-text-area",
                style={"width": "100%", "height": "350px", "display": "block"},
                placeholder="Paste signal here...",
            ),
            Divider().render(),
            AlphaButton("Parse Signal", "parse-trade-btn").render(),
            Divider().render(),
        ],
        id="trade-input-container",
        style={"marginBottom": "1rem"},
    )


def _render_trade_preview(trade_details: TradeDetails) -> html.Div:
    center_style = {"textAlign": "center"}
    digits = len(str(trade_details.entry).split(".")[1]) if "." in str(trade_details.entry) else 0
    stop_loss_distance = round(abs(round(trade_details.stop_loss, digits) - trade_details.entry), digits)
    take_profit_1_distance = round(abs(round(trade_details.take_profit_1, digits) - trade_details.entry), digits)
    take_profit_2_distance = (
        round(abs(round(trade_details.take_profit_2, digits) - trade_details.entry), digits)
        if trade_details.take_profit_2
        else "-"
    )
    take_profit_3_distance = (
        round(abs(round(trade_details.take_profit_3, digits) - trade_details.entry), digits)
        if trade_details.take_profit_3
        else "-"
    )

    return html.Div(
        AlphaCard(
            header=AlphaCardHeader(
                children=[html.H5(f"{trade_details.symbol}@{trade_details.entry}", style=center_style)]
            ).render(),
            body=AlphaCardBody(
                children=[
                    AlphaRow(
                        children=[
                            AlphaCol(
                                children=[
                                    AlphaRow(html.H6("STOP LOSS", style=center_style)),
                                    AlphaRow(
                                        html.H6(
                                            f"{round(trade_details.stop_loss, digits)} (-{stop_loss_distance})",
                                            style={"color": colors.ERROR_COLOR, **center_style},
                                        )
                                    ),
                                ],
                                xs=6,
                                sm=6,
                                md=6,
                                lg=6,
                                xl=6,
                                xxl=6,
                            ),
                            AlphaCol(
                                children=[
                                    AlphaRow(html.H6("TAKE PROFIT", style=center_style)),
                                    AlphaRow(
                                        html.H6(
                                            f"{round(trade_details.take_profit_1, digits)} ({round(take_profit_1_distance, digits)})",  # noqa: E501
                                            style={"color": colors.PRIMARY_COLOR, **center_style},
                                        )
                                    ),
                                    AlphaRow(
                                        html.H6(
                                            f"{round(trade_details.take_profit_2, digits) if trade_details.take_profit_2 else 'n.a.'} ({take_profit_2_distance})",  # noqa: E501
                                            style={"color": colors.PRIMARY_COLOR, **center_style},
                                        )
                                    ),
                                    AlphaRow(
                                        html.H6(
                                            f"{round(trade_details.take_profit_3, digits) if trade_details.take_profit_3 else 'n.a.'} ({take_profit_3_distance})",  # noqa: E501
                                            style={"color": colors.PRIMARY_COLOR, **center_style},
                                        )
                                    ),
                                ],
                                xs=6,
                                sm=6,
                                md=6,
                                lg=6,
                                xl=6,
                                xxl=6,
                            ),
                        ]
                    ),
                ]
            ).render(),
            style={"backgroundColor": "#ffffff"},
        ).render(),
    )


def _render_risk_preview(  # pylint: disable=too-many-locals
    trade_details: TradeDetails, active_levels: Optional[int] = None
) -> html.Div:
    center_style = {"textAlign": "center"}
    all_accounts = AccountService().get_all_accounts()
    configs: List[Tuple[Account, AccountConfig]] = []
    for account in all_accounts:
        if config := AccountConfigService().get_config(account_uid=account.uid, platform_asset_id=trade_details.symbol):
            if config.enabled_trade_direction:
                configs.append((account, config))

    if not configs:
        card_body = AlphaCardBody(
            children=[
                html.H6(
                    f"No Accounts with Symbol={trade_details.symbol} found!",
                    style=center_style | {"marginTop": "1em"},
                )
            ]
        ).render()
    else:
        risk_previews = []
        for account, config in configs:
            total = config.n_staggers
            active = active_levels or total
            active = min(active, total)

            risk_per_trade = config.risk_percent / total
            balance = Mt5Client(secret_id=account.secret_name).get_balance()
            entries = get_stagger_levels(
                trade_details.entry, trade_details.stop_loss, StaggerMethod(config.entry_stagger_method), total
            )[:active]

            sizes = [
                calculate_position_size(
                    entry_price=entry,
                    stop_loss_price=trade_details.stop_loss,
                    percentage_risk=risk_per_trade,
                    balance=balance,
                    asset_type=config.asset_type,
                    decimal_points=config.decimal_points,
                    lot_size=config.lot_size,
                )
                for entry in entries
            ]
            risk_rewards = [
                calculate_risk_reward(entry, trade_details.stop_loss, trade_details.take_profit_1) for entry in entries
            ]
            weighted = [
                calculate_weighted_risk_reward(risk_rewards[: i + 1], sizes[: i + 1]) for i in range(len(entries))
            ]

            risk_previews.append(
                html.Div(
                    [
                        html.H6(account.friendly_name, style={"fontWeight": "bold"}),
                        html.Div(f"Risk %: {config.risk_percent}%"),
                        html.Div(f"Absolute Risk: ${round(balance * config.risk_percent / 100)}"),
                        html.Div(f"Weighted RR: {weighted[-1]:.2f}" if weighted else "Weighted RR: n.a."),
                        Divider().render(),
                    ],
                    style={"marginBottom": "1rem"},
                )
            )

        card_body = AlphaCardBody(children=risk_previews).render()

    return html.Div(
        AlphaCard(
            header=AlphaCardHeader(html.H5("Risk Overview")).render(),
            body=card_body,
            style={"backgroundColor": "#ffffff"},
        ).render()
    )


def _render_trade_details_section() -> List[html.Div]:
    """Render the trade details section."""

    return [
        html.Div(
            [
                AlphaRow(
                    children=[
                        AlphaCol(html.Div(id="parsed-trade-output"), xs=12, sm=12, md=12, lg=6, xl=6, xxl=6),
                        AlphaCol(html.Div(id="parsed-trade-risk-overview"), xs=12, sm=12, md=12, lg=6, xl=6, xxl=6),
                        AlphaCol(html.Div(id="parsed-trade-confluences"), xs=12, sm=12, md=12, lg=6, xl=6, xxl=6),
                    ]
                ),
                AlphaRow(
                    children=[
                        html.Div(
                            [
                                AlphaButton("Execute Trade", "submit-trade-btn").render(),
                            ]
                        ),
                    ]
                ),
            ],
            id="trade-details-section",
            style={"marginBottom": "1.5rem", "display": "none"},
        )
    ]


class NewTradeModal(Molecule):  # pylint: disable=too-few-public-methods
    """A molecule that renders the New Trade modal."""

    def render(self) -> dbc.Modal:
        """Render the New Trade modal."""
        return dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("New Trade")),
                dbc.ModalBody(
                    [_render_trade_input_text_area(), *_render_trade_details_section()],
                    style={"maxHeight": "60vh", "overflowY": "auto"},
                ),
                dbc.ModalFooter([AlphaButton("Close", "close-trade-modal-btn").render()]),
            ],
            id="new-trade-modal",
            is_open=False,
            size="xl",
            keyboard=False,
            backdrop="static",
        )


@callback(
    Output("new-trade-modal", "is_open"),
    Output("trade-input-text-area", "value", allow_duplicate=True),
    Output("parsed-trade-output", "children", allow_duplicate=True),
    Output("parsed-trade-store", "data", allow_duplicate=True),
    Output("submit-trade-btn", "style", allow_duplicate=True),
    Output("trade-input-container", "style", allow_duplicate=True),
    Output("trade-details-section", "style", allow_duplicate=True),
    [
        Input("open-trade-modal-btn", "n_clicks"),
        Input("close-trade-modal-btn", "n_clicks"),
    ],
    State("new-trade-modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_trade_modal(
    _, __, is_open: bool
) -> tuple[bool, str, None, None, Any, Dict[str, str], Dict[str, str], Dict[str, str], Dict[str, str]]:
    """Toggle the trade modal and reset the input fields."""
    return (  # type: ignore
        not is_open,
        "",
        None,
        None,
        HIDDEN,
        {"marginBottom": "1rem", "display": "block"},
        {"marginBottom": "1.5rem", "display": "none"},
    )


@callback(
    Output("parsed-trade-output", "children", allow_duplicate=True),
    Output("parsed-trade-risk-overview", "children", allow_duplicate=True),
    Output("parsed-trade-store", "data", allow_duplicate=True),
    Output("submit-trade-btn", "style", allow_duplicate=True),
    Output("trade-input-container", "style", allow_duplicate=True),
    Output("trade-details-section", "style", allow_duplicate=True),
    Input("parse-trade-btn", "n_clicks"),
    State("trade-input-text-area", "value"),
    prevent_initial_call=True,
)
def parse_trade_signal(_, signal_input: str) -> tuple[Alert, Any, Any, Any, Any, Any, Any]:
    """Parse the trade signal and display the details."""
    if not signal_input:
        return (  # type: ignore
            dbc.Alert("Please paste a signal...", color=colors.WARNING_COLOR),
            dash.no_update,
            dash.no_update,
            HIDDEN,
            dash.no_update,
            dash.no_update,
        )

    try:
        trade_details = TradeMessageParser.parse(signal_input)
    except Exception as error:  # pylint: disable=broad-exception-caught
        CoreLogger().error(f"Failed to parse signal: {error}")
        return (  # type: ignore
            dbc.Alert(f"Error parsing signal: {error}", color=colors.ERROR_COLOR),
            dash.no_update,
            dash.no_update,
            HIDDEN,
            dash.no_update,
            dash.no_update,
        )

    return (  # type: ignore
        _render_trade_preview(trade_details),
        _render_risk_preview(trade_details),
        trade_details.to_dict(),
        AlphaButton("Execute Trade", "submit-trade-btn", hidden=False).default_style,
        {"display": "none"},
        {"marginBottom": "1.5rem", "display": "block"},
    )


@callback(
    Output("trade-status", "children"),
    Input("submit-trade-btn", "n_clicks"),
    State("parsed-trade-store", "data"),
    prevent_initial_call=True,
)
def execute_trade(_, trade_data: Dict[str, Any]) -> dbc.Alert:
    """Execute the trade based on the parsed data."""
    try:
        CoreLogger().info(f"Routing Trade: {trade_data}")
        trade = TradeDetails(**trade_data)
        TradeRouter(trade).route()

        return dbc.Alert("✅ Trade successfully routed!", color=colors.SUCCESS_COLOR, dismissable=True)
    except Exception as error:  # pylint: disable=broad-exception-caught
        CoreLogger().error(f"Execution failed: {error}")

        return dbc.Alert(f"Trade execution failed: {error}", color=colors.ERROR_COLOR, dismissable=True)
