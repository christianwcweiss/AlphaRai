from typing import List, Tuple

import dash
import dash_bootstrap_components as dbc
from components.atoms.buttons.general.button import AlphaButton
from components.atoms.content import MainContent
from components.atoms.divider.divider import Divider
from components.atoms.layout.layout import AlphaCol, AlphaRow
from components.atoms.modal.modal import AlphaModal
from components.atoms.table.table import AlphaTable
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from dash import Input, Output, State, callback, ctx, html
from models.main.general_setting import GeneralSetting
from pages.base_page import BasePage
from pages.settings.settings_render import render_keys_settings_row, render_trade_settings_row
from quant_core.services.core_logger import CoreLogger
from services.db.cache.trade_history import sync_trades_from_all_accounts
from services.db.main.general_setting import delete_setting, get_all_settings, upsert_setting

dash.register_page(__name__, path="/settings", name="Settings")

_REQUIRED_KEYS = {"polygon_api_key"}


class GeneralSettingsPage(BasePage):  # pylint: disable=too-few-public-methods
    """General Settings Page."""

    def render(self):
        """Render the page layout."""
        return PageBody(
            [
                PageHeader("General Settings").render(),
                MainContent(
                    [
                        render_trade_settings_row(),
                        Divider().render(),
                        render_keys_settings_row(),
                        Divider().render(),
                        AlphaButton("Sync Trades from TradingView", "sync-trades-btn").render(),
                        html.Div(id="sync-trades-status", className="mt-3"),
                    ]
                ),
            ]
        )


layout = GeneralSettingsPage("General Settings").layout
