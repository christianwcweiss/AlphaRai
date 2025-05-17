import dash
from dash import html

from components.atoms.card.card import AlphaCard
from components.atoms.content import MainContent
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from pages.base_page import BasePage
from services.db.bots.grid_bot import get_all_grid_bots

dash.register_page(__name__, path="/bots/grid-bots", name="Grid Bots")


class GridBotsPage(BasePage):  # pylint: disable=too-few-public-methods
    """Grid Bots Page."""

    def render(self) -> html.Div:
        bots = get_all_grid_bots()

        return PageBody(
            [
                html.Div(id="page-init", style={"display": "none"}),
                PageHeader("Grid Bots").render(),
                MainContent(
                    [
                        AlphaRow(
                            [
                                AlphaCol(
                                    AlphaCard(
                                        title="➕ New Grid Bot",
                                        subtitle="Create a new grid trading bot.",
                                        href="/bots/grid-bots/new",
                                    ).render()
                                )
                            ]
                        ),
                        AlphaRow(
                            [
                                AlphaCol(
                                    AlphaCard(
                                        title=bot.name,
                                        subtitle=f"{bot.symbol} "
                                        f"• {bot.n_grids} grids "
                                        f"• {'Enabled' if bot.enabled else 'Disabled'}",
                                        href=f"/bots/grid-bots/{bot.uid}",
                                    ).render()
                                )
                                for bot in bots
                            ]
                        ),
                    ]
                ),
            ]
        )


page = GridBotsPage("Grid Bots")
layout = page.layout
