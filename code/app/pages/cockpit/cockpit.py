import dash
from components.atoms.buttons.general.button import AlphaButton
from components.atoms.content import MainContent
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from dash import dcc, html
from pages.base_page import BasePage
from pages.cockpit.cockpit_callbacks import (  # pylint: disable=unused-import # noqa: F401
    control_bot_and_toggle_accounts,
)
from pages.cockpit.cockpit_constants import (
    BOT_CONTROLS_CONTAINER,
    BOT_STATUS_INTERVAL_ID,
    START_BOT_BTN_ID,
    STOP_BOT_BTN_ID,
)
from pages.cockpit.cockpit_render import render_account_management_row, render_tv_calendar_row
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
                        dcc.Interval(id=BOT_STATUS_INTERVAL_ID, interval=2000, n_intervals=0),
                        html.Div(id=BOT_CONTROLS_CONTAINER),
                        AlphaButton(
                            label="Placeholder for Bot Controls", button_id=START_BOT_BTN_ID, hidden=True
                        ).render(),
                        AlphaButton(
                            label="Placeholder for Bot Controls", button_id=STOP_BOT_BTN_ID, hidden=True
                        ).render(),
                        render_account_management_row(),
                        render_tv_calendar_row(),
                    ]
                ),
            ]
        )


layout = CockpitPage("Cockpit").layout
