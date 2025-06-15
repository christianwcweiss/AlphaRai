import dash
from components.atoms.buttons.general.button import AlphaButton
from components.atoms.content import MainContent
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from dash import html
from pages.base_page import BasePage
from pages.cockpit.cockpit_callbacks import download_signals  # pylint: disable=unused-import  # noqa: F401
from pages.cockpit.cockpit_render import render_signal_timeline
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
                        html.Div(
                            className="d-flex justify-content-end mb-3",
                            children=[
                                AlphaButton(label="Download all signals", button_id="download-signals-btn").render(),
                                html.Div(id="download-signals-status", className="ms-3 text-success fw-bold"),
                            ],
                        ),
                        html.Div(
                            children=[
                                html.H2("Trading Cockpit"),
                                html.Div(id="signal-timeline-container", children=render_signal_timeline()),
                            ],
                            style={"padding": "1rem"},
                        ),
                    ]
                ),
            ]
        )


layout = CockpitPage("Cockpit").layout
