import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from components.atoms.content import MainContent
from components.atoms.divider.divider import Divider
from components.atoms.layout.layout import AlphaCol, AlphaRow
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from constants.style import HIDDEN
from pages.accounts.account_details.account_details_callbacks import sync_symbols_callback
from pages.accounts.account_details.account_details_callbacks import render_config_cards
from pages.accounts.account_details.account_details_callbacks import extract_uid_from_url
from pages.accounts.account_details.account_details_callbacks import save_config
from pages.accounts.account_details.account_details_callbacks import open_edit_modal
from pages.accounts.account_details.account_details_constants import CARD_CONTAINER, DYNAMIC_HEADER, SETTINGS_UID, \
    SETTINGS_URL
from pages.accounts.account_details.account_details_render import render_symbol_sync_button, render_edit_modal

from pages.base_page import BasePage


dash.register_page(__name__, path_template="/accounts/<uid>", name="Account Details")



class AccountDetailsPage(BasePage):
    """Settings Details Page."""
    def render(self):
        """Render the Account Details Page."""
        return PageBody(
            [
                dcc.Location(id=SETTINGS_URL),
                html.Div(id=SETTINGS_UID, style=HIDDEN),
                html.Div(id=DYNAMIC_HEADER),
                render_edit_modal(),
                MainContent(
                    [
                        AlphaRow(
                            [
                                render_symbol_sync_button()
                            ]
                        ),
                        AlphaRow(
                            html.Div(id=CARD_CONTAINER),
                        ),
                        Divider().render(),
                    ]
                ),
            ]
        )


layout = AccountDetailsPage("Account Details").layout
