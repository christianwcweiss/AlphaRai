import dash
from dash import html

from components.atoms.card.card import AlphaCard
from components.atoms.content import MainContent
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from pages.base_page import BasePage

dash.register_page(__name__, path="/settings", name="Settings")

SETTING_CARDS = [
    ("Accounts", "/settings/accounts"),
    ("General", "/settings/general"),
    ("Confluences", "/settings/confluences"),
]


class SettingsPage(BasePage):
    def render(self):
        return PageBody(
            [
                html.Div(id="page-init", style={"display": "none"}),
                PageHeader("Settings").render(),
                MainContent(
                    [
                        AlphaRow(
                            [
                                AlphaCol(
                                    AlphaCard(
                                        title=title,
                                        href=href,
                                        aspect_ratio="1",
                                    ).render(),
                                    xs=12,
                                    sm=12,
                                    md=6,
                                    lg=4,
                                    xl=4,
                                ) for title, href in SETTING_CARDS
                            ]
                        )
                    ]
                ),
            ]
        )


page = SettingsPage("Settings")
layout = page.layout
