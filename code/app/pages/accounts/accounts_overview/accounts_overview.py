import dash
import dash_bootstrap_components as dbc
from components.atoms.buttons.general.button import AlphaButton, AlphaButtonColor
from components.atoms.content import MainContent
from components.atoms.divider.divider import Divider
from components.atoms.layout.layout import AlphaCol, AlphaRow
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from constants import colors
from dash import dcc, html
from pages.accounts.accounts_overview.accounts_overview_callbacks import (  # type: ignore  # pylint: disable=unused-import  # noqa: E501, F401
    load_mt5_credentials_on_page_load,
    manage_delete,
    save_new_account,
    toggle_add_modal,
)
from pages.accounts.accounts_overview.accounts_overview_constants import (
    ADD_ACCOUNT_BUTTON_LABEL,
    ADD_ACCOUNT_CANCEL_BUTTON_ID,
    ADD_ACCOUNT_CANCEL_BUTTON_LABEL,
    ADD_ACCOUNT_CONFIRM_BUTTON_ID,
    ADD_ACCOUNT_CONFIRM_BUTTON_LABEL,
    ADD_ACCOUNT_MODAL_ID,
    ADD_ACCOUNT_MODAL_TITLE,
    CONTENT_ROWS,
    DELETE_ACCOUNT_MODAL_BODY,
    DELETE_ACCOUNT_MODAL_CANCEL_BUTTON_ID,
    DELETE_ACCOUNT_MODAL_CANCEL_BUTTON_LABEL,
    DELETE_ACCOUNT_MODAL_CONFIRM_BUTTON_ID,
    DELETE_ACCOUNT_MODAL_CONFIRM_BUTTON_LABEL,
    DELETE_ACCOUNT_MODAL_ID,
    DELETE_ACCOUNT_MODAL_TITLE,
    INPUT_ACCOUNT_NAME_ID,
    INPUT_ACCOUNT_NAME_LABEL,
    INPUT_ACCOUNT_SECRET_ID,
    INPUT_ACCOUNT_SECRET_LABEL,
    INPUT_PLATFORM_ID,
    INPUT_PLATFORM_LABEL,
    INPUT_PROP_FIRM,
    INPUT_PROP_FIRM_LABEL,
    LOADING_PAGE_ID,
    OPEN_ADD_ACCOUNT_MODAL_ID,
    PAGE_INIT,
    PENDING_DELETE_UID_ID,
    PLATFORM_OPTIONS,
    PROP_FIRM_OPTIONS,
)
from pages.base_page import BasePage

dash.register_page(__name__, path="/accounts", name="Accounts")


class AccountsPage(BasePage):
    """Accounts Page."""

    def _render_delete_account_modal(self) -> html.Div:
        return html.Div(
            children=[
                dcc.Store(id=PENDING_DELETE_UID_ID),
                dbc.Modal(
                    id=DELETE_ACCOUNT_MODAL_ID,
                    is_open=False,
                    children=[
                        dbc.ModalHeader(DELETE_ACCOUNT_MODAL_TITLE),
                        dbc.ModalBody(DELETE_ACCOUNT_MODAL_BODY),
                        dbc.ModalFooter(
                            [
                                AlphaButton(
                                    DELETE_ACCOUNT_MODAL_CONFIRM_BUTTON_LABEL,
                                    button_id=DELETE_ACCOUNT_MODAL_CONFIRM_BUTTON_ID,
                                ).render(),
                                AlphaButton(
                                    DELETE_ACCOUNT_MODAL_CANCEL_BUTTON_LABEL,
                                    button_id=DELETE_ACCOUNT_MODAL_CANCEL_BUTTON_ID,
                                ).render(),
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
                    id=ADD_ACCOUNT_MODAL_ID,
                    is_open=False,
                    children=[
                        dbc.ModalHeader(dbc.ModalTitle(ADD_ACCOUNT_MODAL_TITLE)),
                        dbc.ModalBody(
                            children=[
                                dbc.Input(
                                    id=INPUT_ACCOUNT_NAME_ID,
                                    placeholder=INPUT_ACCOUNT_NAME_LABEL,
                                    type="text",
                                    className="mb-2",
                                ),
                                dbc.Input(
                                    id=INPUT_ACCOUNT_SECRET_ID,
                                    placeholder=INPUT_ACCOUNT_SECRET_LABEL,
                                    type="text",
                                    className="mb-2",
                                ),
                                dbc.Select(
                                    id=INPUT_PLATFORM_ID,
                                    options=PLATFORM_OPTIONS,
                                    placeholder=INPUT_PLATFORM_LABEL,
                                    className="mb-2",
                                ),
                                dbc.Select(
                                    id=INPUT_PROP_FIRM,
                                    options=PROP_FIRM_OPTIONS,
                                    placeholder=INPUT_PROP_FIRM_LABEL,
                                    className="mb-2",
                                ),
                                AlphaRow(
                                    children=[
                                        AlphaCol(
                                            AlphaButton(
                                                button_id=ADD_ACCOUNT_CONFIRM_BUTTON_ID,
                                                label=ADD_ACCOUNT_CONFIRM_BUTTON_LABEL,
                                                button_color=AlphaButtonColor.CONFIRM,
                                            ).render(),
                                            xs=12,
                                            sm=6,
                                            md=6,
                                            lg=6,
                                            xl=6,
                                        ),
                                        AlphaCol(
                                            AlphaButton(
                                                button_id=ADD_ACCOUNT_CANCEL_BUTTON_ID,
                                                label=ADD_ACCOUNT_CANCEL_BUTTON_LABEL,
                                                button_color=AlphaButtonColor.CANCEL,
                                            ).render(),
                                            xs=12,
                                            sm=6,
                                            md=6,
                                            lg=6,
                                            xl=6,
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ],
                ),
                Divider().render(),
            ]
        )

    def render(self) -> PageBody:
        """Render the Accounts Page."""
        return PageBody(
            [
                html.Div(id=PAGE_INIT, children="trigger", style={"display": "none"}),
                PageHeader("Accounts").render(),
                MainContent(
                    [
                        dcc.Loading(
                            id=LOADING_PAGE_ID,
                            type="circle",
                            children=html.Div(id=CONTENT_ROWS, style={"marginTop": "20px"}),
                        ),
                        AlphaButton(
                            button_id=OPEN_ADD_ACCOUNT_MODAL_ID,
                            label=ADD_ACCOUNT_BUTTON_LABEL,
                        ).render(),
                        self._render_add_account_modal(),
                        self._render_delete_account_modal(),
                    ]
                ),
            ]
        )


page = AccountsPage("Accounts")
layout = page.layout
