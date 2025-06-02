from typing import Tuple, List, Dict, Any

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc
from dash.development.base_component import Component

from components.atoms.card.card import AlphaCard
from components.atoms.divider.divider import Divider
from components.atoms.layout.layout import AlphaCol, AlphaRow
from components.atoms.text.subsubsection import SubSubsectionHeader
from components.molecules.molecule import Molecule
from services.db.cache.trade_history import get_all_trades_df


def analytics_bar_get_active_states(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    group_by_account_id: bool,
    group_by_symbol: bool,
    group_by_asset_type: bool,
    group_by_direction: bool,
    group_by_hour: bool,
    group_by_weekday: bool,
    abs_active: bool,
    rel_active: bool,
    trigger_id: str,
    prefix: str = "",
) -> List[bool]:
    """Get the active states of the group by and view mode buttons based on the trigger ID."""
    if trigger_id == f"{prefix}-group-by-account-id":
        group_by_account_id = not group_by_account_id
    elif trigger_id == f"{prefix}-group-by-symbol":
        group_by_symbol = not group_by_symbol
    elif trigger_id == f"{prefix}-group-by-asset-type":
        group_by_asset_type = not group_by_asset_type
    elif trigger_id == f"{prefix}-group-by-direction":
        group_by_direction = not group_by_direction
    elif trigger_id == f"{prefix}-group-by-hour":
        group_by_hour = not group_by_hour
    elif trigger_id == f"{prefix}-group-by-weekday":
        group_by_weekday = not group_by_weekday

    if trigger_id in (f"{prefix}-show-abs-values", f"{prefix}-show-rel-values"):
        abs_active = trigger_id == f"{prefix}-show-abs-values"
        rel_active = trigger_id == f"{prefix}-show-rel-values"
    elif not abs_active and not rel_active:
        abs_active = True

    return [
        group_by_account_id,
        group_by_symbol,
        group_by_asset_type,
        group_by_direction,
        group_by_hour,
        group_by_weekday,
        abs_active,
        rel_active,
    ]


def analytics_bar_filter_trades(
    trades_df: pd.DataFrame,
    account_ids: List[str],
    symbols: List[str],
    asset_types: List[str],
) -> pd.DataFrame:
    """Filter trades based on the selected account IDs, symbols, and asset types."""
    if account_ids:
        trades_df = trades_df[trades_df["account_id"].isin(account_ids)]
    if symbols:
        trades_df = trades_df[trades_df["symbol"].isin(symbols)]
    if asset_types:
        trades_df = trades_df[trades_df["asset_type"].isin(asset_types)]

    return trades_df


class AnalyticsToolbarMolecule(Molecule):  # pylint: disable=too-few-public-methods
    """Toolbar for the analysis pages."""

    def __init__(self, prefix: str = "") -> None:
        self._prefix = prefix
        self._filters = [
            ("Account ID", f"{self._prefix}-filter-by-account-id"),
            ("Symbol", f"{self._prefix}-filter-by-symbol"),
            ("Asset Type", f"{self._prefix}-filter-by-asset-type"),
        ]
        self._groups = [
            ("Account ID", f"{self._prefix}-group-by-account-id"),
            ("Symbol", f"{self._prefix}-group-by-symbol"),
            ("Asset Type", f"{self._prefix}-group-by-asset-type"),
            ("Direction", f"{self._prefix}-group-by-direction"),
            ("Hour of Day", f"{self._prefix}-group-by-hour"),
            ("Day of Week", f"{self._prefix}-group-by-weekday"),
        ]
        self._view_modes = [
            ("Absolute", f"{self._prefix}-show-abs-values"),
            ("Relative", f"{self._prefix}-show-rel-values"),
        ]

    STYLE = {"marginBottom": "20px"}

    def _load_filter_options(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Load filter options for the dropdowns."""
        trades_df = get_all_trades_df()
        if trades_df.empty:
            return [], [], []

        account_ids = [account_id for account_id in trades_df["account_id"].unique() if isinstance(account_id, str)]
        symbols = [symbol for symbol in trades_df["symbol"].unique() if isinstance(symbol, str)]
        asset_types = [asset_type for asset_type in trades_df["asset_type"].unique() if isinstance(asset_type, str)]

        return (
            [{"label": val, "value": val} for val in sorted(account_ids)],
            [{"label": val, "value": val} for val in sorted(symbols)],
            [{"label": val, "value": val} for val in sorted(asset_types)],
        )

    def _render_filter_dropdowns(self) -> html.Div:
        """Render the filter dropdowns."""
        account_options, symbol_options, asset_type_options = self._load_filter_options()
        dropdown_options = {
            f"{self._prefix}-filter-by-account-id": account_options,
            f"{self._prefix}-filter-by-symbol": symbol_options,
            f"{self._prefix}-filter-by-asset-type": asset_type_options,
        }

        return html.Div(
            [
                AlphaRow(
                    children=[
                        SubSubsectionHeader(
                            "FILTERS",
                            style={"marginTop": "0px", "paddingTop": "0px"},
                        ).render()
                    ]
                ),
                AlphaRow(
                    children=[
                        AlphaCol(
                            children=[
                                html.Label(label, htmlFor=dropdown_id),
                                dcc.Dropdown(
                                    id=dropdown_id,
                                    options=dropdown_options.get(dropdown_id, []),
                                    multi=True,
                                    placeholder=f"Select {label}",
                                ),
                            ],
                            sm=12,
                            md=6,
                            lg=4,
                            xl=4,
                        )
                        for label, dropdown_id in self._filters
                    ],
                    style={"alignItems": "center"},
                ),
            ]
        )

    def _render_group_by_buttons(self) -> html.Div:
        return html.Div(
            [
                AlphaRow(
                    children=[
                        SubSubsectionHeader(
                            "GROUP BY",
                            style={"marginTop": "0px", "paddingTop": "0px"},
                        ).render()
                    ],
                ),
                AlphaRow(
                    children=[
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    label,
                                    id=button_id,
                                    color="secondary",
                                    outline=True,
                                    active=False,
                                    n_clicks=0,
                                )
                                for label, button_id in self._groups
                            ],
                            size="sm",
                        )
                    ]
                ),
            ],
        )

    def _render_view_mode_buttons(self) -> html.Div:
        return html.Div(
            [
                AlphaRow(
                    children=[
                        SubSubsectionHeader(
                            "VIEW MODE",
                            style={"marginTop": "0px", "paddingTop": "0px"},
                        ).render()
                    ],
                ),
                AlphaRow(
                    children=[
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    label,
                                    id=button_id,
                                    color="secondary",
                                    outline=True,
                                    active=False,
                                    n_clicks=0,
                                )
                                for label, button_id in self._view_modes
                            ],
                            size="sm",
                        )
                    ]
                ),
            ],
        )

    def render(self) -> Component:
        return html.Div(
            AlphaCard(
                children=[
                    self._render_filter_dropdowns(),
                    Divider().render(),
                    self._render_group_by_buttons(),
                    Divider().render(),
                    self._render_view_mode_buttons(),
                ],
                show_divider=False,
                style={"backgroundColor": "#ffffff"},
            ).render(),
            style=self.STYLE,
        )
