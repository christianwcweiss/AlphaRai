import dash
from dash import html, Input, Output, State, ctx, callback

from components.atoms.buttons.general.button import AlphaButton
from components.atoms.content import MainContent
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.atoms.text.page import PageHeader
from components.atoms.text.section import SectionHeader
from components.frame.body import PageBody
from constants import colors
from models.account import Account
from pages.base_page import BasePage
from services.db.account import get_all_accounts, toggle_account_enabled

COCKPIT_PATH = "/"
dash.register_page(__name__, path=COCKPIT_PATH, name="Cockpit")


def render_account_card(account: Account) -> AlphaCol:
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
    accounts = get_all_accounts()
    return AlphaRow([render_account_card(account) for account in accounts])


class CockpitPage(BasePage):
    def render(self):
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
def toggle_accounts(_, __):
    if not ctx.triggered_id:
        return render_account_cards()
    toggle_account_enabled(ctx.triggered_id["index"])
    return render_account_cards()
