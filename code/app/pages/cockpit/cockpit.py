import dash
from dash import html, dcc, Input, Output, State, ctx, callback
from components.atoms.buttons.general.button import AlphaButton
from components.atoms.content import MainContent
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.atoms.text.page import PageHeader
from components.atoms.text.section import SectionHeader
from components.frame.body import PageBody
from constants import colors
from models.main.account import Account
from pages.base_page import BasePage
from services.db.main.account import get_all_accounts, toggle_account_enabled
from services.relay_bot import DiscordRelayBot

COCKPIT_PATH = "/"
dash.register_page(__name__, path=COCKPIT_PATH, name="Cockpit")

bot_instance = DiscordRelayBot()


def render_account_card(account: Account) -> AlphaCol:
    """Render a card for a given account with a toggle button."""
    return AlphaCol(
        AlphaButton(
            label=f"{account.platform} {account.friendly_name}",
            button_id={"type": "account-toggle", "index": account.uid},
            style={
                "backgroundColor": (colors.PRIMARY_COLOR if account.enabled else colors.ERROR_COLOR),
            },
        ).render(),
        xs=12,
        sm=6,
        md=6,
        lg=4,
        xl=4,
    )


def render_account_cards() -> AlphaRow:
    """Render a row of account cards based on the current accounts in the database."""
    accounts = get_all_accounts()
    return AlphaRow([render_account_card(account) for account in accounts])


def render_bot_controls(bot_running: bool) -> html.Div:
    """Render the controls for the Discord bot, including start and stop buttons."""
    return html.Div(
        [
            AlphaButton(
                "Bot Running ✅" if bot_running else "Start Discord Bot",
                button_id="start-bot",
                style={
                    "backgroundColor": (colors.SUCCESS_COLOR if bot_running else colors.PRIMARY_COLOR),
                },
            ).render(),
            AlphaButton(
                "Stop Discord Bot",
                button_id="stop-bot",
                style={
                    "backgroundColor": colors.ERROR_COLOR,
                    "opacity": 1.0 if bot_running else 0.5,
                    "pointerEvents": "auto" if bot_running else "none",
                },
            ).render(),
        ],
        style={"marginBottom": "20px"},
    )


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


@callback(
    Output("account-toggle-container", "children"),
    Input("start-bot", "n_clicks"),
    Input("stop-bot", "n_clicks"),
    Input({"type": "account-toggle", "index": dash.ALL}, "n_clicks"),
    State({"type": "account-toggle", "index": dash.ALL}, "id"),
    prevent_initial_call=True,
)
def control_bot_and_toggle_accounts(_, __, ___, ____):
    """Control the Discord bot and toggle account states based on user interactions."""
    triggered = ctx.triggered_id

    if triggered == "start-bot":
        bot_instance.run()

    elif triggered == "stop-bot":
        bot_instance.stop()

    elif isinstance(triggered, dict) and triggered.get("type") == "account-toggle":
        toggle_account_enabled(triggered["index"])

    return render_account_cards()


@callback(
    Output("bot-controls-container", "children"),
    Input("bot-status-interval", "n_intervals"),
)
def update_bot_status(_):
    """Update the bot controls based on the current status of the Discord bot."""
    return render_bot_controls(bot_instance.is_running())
