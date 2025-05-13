import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

from components.atoms.buttons.general.button import AlphaButton
from components.atoms.content import MainContent
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from pages.accounts.accounts_overview.accounts_overview_callbacks import load_mt5_credentials_on_page_load  # type: ignore  # pylint: disable=unused-import  # noqa: E501, F401
from pages.accounts.accounts_overview.accounts_overview_callbacks import manage_delete  # type: ignore  # pylint: disable=unused-import  # noqa: E501, F401
from pages.accounts.accounts_overview.accounts_overview_callbacks import save_new_account  # type: ignore  # pylint: disable=unused-import  # noqa: E501, F401
from pages.accounts.accounts_overview.accounts_overview_callbacks import toggle_add_modal  # type: ignore  # pylint: disable=unused-import  # noqa: E501, F401
from pages.base_page import BasePage

dash.register_page(__name__, path="/accounts", name="Accounts")


class AccountsPage(BasePage):
    """Accounts Page."""

    def _render_delete_account_modal(self) -> html.Div:
        return html.Div(
            children=[
                dcc.Store(id="pending-delete-uid"),
                dbc.Modal(
                    id="delete-confirm-modal",
                    is_open=False,
                    children=[
                        dbc.ModalHeader("Confirm Deletion"),
                        dbc.ModalBody("Are you sure you want to delete this account?"),
                        dbc.ModalFooter(
                            [
                                dbc.Button("Delete", id="confirm-delete-btn", color="danger"),
                                dbc.Button("Cancel", id="cancel-delete-btn", color="secondary", className="ms-2"),
                            ]
                        ),
                    ],
                ),
            ]
        )

    def _render_add_account_modal(self) -> html.Div:
        return html.Div(
            children=[
                dbc.Modal(
                    id="add-account-modal",
                    is_open=False,
                    children=[
                        dbc.ModalHeader(dbc.ModalTitle("➕ Add New MT5 Account")),
                        dbc.ModalBody(
                            [
                                dbc.Input(
                                    id="input-account-name",
                                    placeholder="Friendly Name",
                                    type="text",
                                    className="mb-2",
                                ),
                                dbc.Input(id="input-account-secret", placeholder="AWS Secret Name", type="text"),
                            ]
                        ),
                    ],
                ),
                html.Hr(),
            ]
        )

    def render(self) -> PageBody:
        """Render the Accounts Page."""
        return PageBody(
            [
                html.Div(id="page-init", children="trigger", style={"display": "none"}),
                PageHeader("Accounts").render(),
                MainContent(
                    [
                        dcc.Loading(
                            id="loading-accounts",
                            type="circle",
                            children=html.Div(id="mt5-rows", style={"marginTop": "20px"}),
                        ),
                        AlphaButton(label="➕ Add MT5 Account", button_id="open-add-mt5-btn").render(),
                        self._render_add_account_modal(),
                        self._render_delete_account_modal(),
                    ]
                ),
            ]
        )


page = AccountsPage("Accounts")
layout = page.layout
