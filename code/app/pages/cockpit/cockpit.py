import dash
from components.atoms.content import MainContent
from components.atoms.text.page import PageHeader
from components.atoms.text.section import SectionHeader
from components.frame.body import PageBody
from dash import dcc, html
from pages.base_page import BasePage
from pages.cockpit.cockpit_callbacks import control_bot_and_toggle_accounts, update_bot_status
from services.relay_bot import DiscordRelayBot

COCKPIT_PATH = "/"
dash.register_page(__name__, path=COCKPIT_PATH, name="Cockpit")

bot_instance = DiscordRelayBot()


class CockpitPage(BasePage):
    """CockpitPage is a Dash page that provides a control panel for managing the Discord bot and accounts."""

    def render(self):
        return PageBody(
            [
                PageHeader(self._title).render(),
                MainContent(
                    [
                        SectionHeader("Discord Bot Control").render(),
                        dcc.Interval(id="bot-status-interval", interval=2000, n_intervals=0),
                        html.Div(id="bot-controls-container"),
                        SectionHeader("Account Management").render(),
                        html.Div(id="account-toggle-container"),
                    ]
                ),
            ]
        )


layout = CockpitPage("Cockpit").layout
