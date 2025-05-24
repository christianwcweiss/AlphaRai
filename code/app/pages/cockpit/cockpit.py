import dash
from dash import html, Input, Output, State, ctx, callback

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

COCKPIT_PATH = "/"
dash.register_page(__name__, path=COCKPIT_PATH, name="Cockpit")


def render_account_card(account: Account) -> AlphaCol:
    """Render a single account card."""
    return AlphaCol(
        AlphaButton(
            label=f"{account.platform} {account.friendly_name}",
            button_id={"type": "account-toggle", "index": account.uid},
            style={"backgroundColor": colors.PRIMARY_COLOR if account.enabled else colors.ERROR_COLOR},
        ).render(),
        xs=12,
        sm=6,
        md=6,
        lg=4,
        xl=4,
    )


def render_account_cards() -> AlphaRow:
    """Render account cards based on the current accounts."""
    accounts = get_all_accounts()
    return AlphaRow([render_account_card(account) for account in accounts])


class CockpitPage(BasePage):  # pylint: disable=too-few-public-methods
    """Cockpit Page."""

    def render(self):
        """Render the cockpit page."""
        return PageBody(
            [
                PageHeader(self._title).render(),
                MainContent(
                    [
                        SectionHeader("Account Management").render(),
                        html.Div(render_account_cards(), id="account-toggle-container"),
                    ]
                ),
            ]
        )


layout = CockpitPage("Cockpit").layout


@callback(
    Output("account-toggle-container", "children"),
    Input({"type": "account-toggle", "index": dash.ALL}, "n_clicks"),
    State({"type": "account-toggle", "index": dash.ALL}, "id"),
)
def toggle_accounts(_, __) -> AlphaRow:
    """Toggle account enabled state."""
    if not ctx.triggered_id:
        return render_account_cards()

    toggle_account_enabled(ctx.triggered_id["index"])

    return render_account_cards()
