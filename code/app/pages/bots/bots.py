import dash
from dash import html

from components.atoms.card.card import AlphaCard
from components.atoms.content import MainContent
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from pages.base_page import BasePage

dash.register_page(__name__, path="/bots", name="Bots")



class BotsPage(BasePage):
    def render(self):
        return PageBody(
            [
                html.Div(id="page-init", style={"display": "none"}),
                PageHeader("Bots").render(),
                MainContent(
                    [
                        html.Div("Coming soon..."),
                    ]
                ),
            ]
        )


page = BotsPage("Settings")
layout = page.layout
