import dash
from components.atoms.buttons.general.button import AlphaButton
from components.atoms.content import MainContent
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from dash import dcc, html
from pages.base_page import BasePage
from pages.settings.settings_callbacks import (  # pylint: disable=unused-import  # noqa: F401
    load_polygon_api_key,
    load_trade_window_settings,
    save_polygon_api_key,
    save_trade_window_settings,
    sync_trades_from_metatrader_5,
)
from pages.settings.settings_contants import POLYGON_API_KEY_STORE_ID
from pages.settings.settings_render import render_keys_settings_card, render_trade_settings_card

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
                        render_trade_settings_card(),
                        render_keys_settings_card(),
                        dcc.Store(id="trade-window-store"),
                        dcc.Store(id=POLYGON_API_KEY_STORE_ID),
                        # deprecated sync trades button -> move to analytics page
                        AlphaButton("Sync Trades from TradingView", "sync-trades-btn").render(),
                        html.Div(id="sync-trades-status", className="mt-3"),
                    ]
                ),
            ]
        )


layout = GeneralSettingsPage("General Settings").layout
