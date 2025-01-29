import dash
from dash import html, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc

from components.atoms.content import MainContent
from components.atoms.header import PageHeader
from components.frame.body import PageBody
from pages.base_page import BasePage
from services.credential_settings import get_all_credential_settings, toggle_credential_enabled

dash.register_page(__name__, path="/", name="Cockpit")


def build_account_buttons(accounts):
    return [
        dbc.Button(
            html.Div([
                html.Div(acc.friendly_name or acc.uid),
                html.Small(
                    "ENABLED" if acc.enabled else "DISABLED",
                    style={"fontSize": "0.7rem", "color": "#f8f9fa" if acc.enabled else "#f8d7da"},
                )
            ]),
            id={"type": "account-toggle", "index": acc.uid},
            color="success" if acc.enabled else "danger",
            className="m-1",
            n_clicks=0,
            style={"width": "150px", "height": "60px"},
        ) for acc in accounts
    ]

class CockpitPage(BasePage):
    def render(self):
        # Fetch account data via service
        accounts = get_all_credential_settings()

        account_buttons = build_account_buttons(accounts)

        return PageBody([
            PageHeader(f"{self.title}"),
            MainContent([
                html.H5("Connected Accounts"),
                html.Div(account_buttons, id="account-toggle-container")
            ])
        ])


# Create the page instance and export the layout
page = CockpitPage(title="Cockpit")
layout = page.layout


# Callback to toggle account "enabled" flag on click
@callback(
    Output("account-toggle-container", "children"),
    Input({"type": "account-toggle", "index": dash.ALL}, "n_clicks"),
    State({"type": "account-toggle", "index": dash.ALL}, "id"),
)
def toggle_accounts(n_clicks_list, id_list):
    if not ctx.triggered_id:
        raise dash.exceptions.PreventUpdate

    triggered_uid = ctx.triggered_id["index"]

    # Toggle the status via service
    toggle_credential_enabled(triggered_uid)

    # Re-fetch all accounts and rebuild buttons
    accounts = get_all_credential_settings()

    return build_account_buttons(accounts)
