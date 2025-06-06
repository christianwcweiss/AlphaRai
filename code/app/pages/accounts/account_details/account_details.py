import dash
from components.atoms.content import MainContent
from components.atoms.divider.divider import Divider
from components.atoms.layout.layout import AlphaRow
from components.frame.body import PageBody
from constants.style import HIDDEN
from dash import dcc, html
from pages.accounts.account_details.account_details_callbacks import (  # pylint: disable=unused-import  # noqa: F401
    extract_uid_from_url,
    open_edit_modal,
    render_config_cards,
    save_config,
    sync_symbols_callback,
)
from pages.accounts.account_details.account_details_constants import (
    CARD_CONTAINER,
    DYNAMIC_HEADER,
    SETTINGS_UID,
    SETTINGS_URL,
)
from pages.accounts.account_details.account_details_render import render_edit_modal, render_symbol_sync_button
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
                        AlphaRow([render_symbol_sync_button()]),
                        AlphaRow(
                            html.Div(id=CARD_CONTAINER),
                        ),
                        Divider().render(),
                    ]
                ),
            ]
        )


layout = AccountDetailsPage("Account Details").layout
