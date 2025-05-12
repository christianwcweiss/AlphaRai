import dash
from dash import html, dcc

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
                        AlphaRow(
                            [
                                AlphaCol(
                                    AlphaCard(
                                        title="Grid Bots",
                                        subtitle="View and manage your grid trading bots.",
                                        href="/bots/grid-bots",
                                    ).render()
                                ),
                            ]
                        ),
                    ]
                ),
            ]
        )


page = BotsPage("Bots")
layout = page.layout