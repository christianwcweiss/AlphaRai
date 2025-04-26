import dash
import dash_bootstrap_components as dbc
from dash import html

from components.atoms.card.card import AlphaCard
from components.atoms.content import MainContent
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from pages.base_page import BasePage

dash.register_page(__name__, path="/settings", name="Settings")


class SettingsPage(BasePage):
    def render(self):
        return PageBody(
            [
                html.Div(id="page-init", style={"display": "none"}),  # Triggers page load
                PageHeader("Settings"),
                MainContent(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    AlphaCard(
                                        title="Accounts",
                                        href="/settings/accounts",
                                        children=[],
                                        aspect_ratio="1:1",
                                        height="200px",
                                    ).render(),
                                    xs=12,
                                    sm=12,
                                    md=6,
                                    lg=4,
                                    xl=4,
                                ),
                                dbc.Col(
                                    AlphaCard(
                                        title="Strategies",
                                        href="/settings/strategies",
                                        children=[],
                                        aspect_ratio="1:1",
                                        height="200px",
                                    ).render(),
                                    xs=12,
                                    sm=12,
                                    md=6,
                                    lg=4,
                                    xl=4,
                                )
                            ]
                        )
                    ]
                ),
            ]
        )


page = SettingsPage("Settings")
layout = page.layout
