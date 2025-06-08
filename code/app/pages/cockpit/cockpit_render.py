import os.path

from components.atoms.buttons.general.button import AlphaButton, AlphaButtonColor
from components.atoms.layout.layout import AlphaCol, AlphaRow
from dash import html
from models.main.account import Account
from pages.cockpit.cockpit_constants import (
    ACCOUNT_TOGGLE_ID,
    BOT_RUNNING_LABEL,
    START_BOT_BTN_ID,
    START_BOT_BTN_LABEL,
    STOP_BOT_BTN_ID,
    STOP_BOT_BTN_LABEL,
)
from services.db.main.account import AccountService


def render_account_card(account: Account) -> html.Div:
    """Render a card for a given account with a toggle button."""
    return AlphaButton(
        label=f"{account.prop_firm.value} | {account.friendly_name}",
        button_id={"type": ACCOUNT_TOGGLE_ID, "index": account.uid},
        button_color=AlphaButtonColor.SUCCESS if account.enabled else AlphaButtonColor.ERROR,
        height="70px",
    ).render()


def render_account_cards() -> AlphaRow:
    """Render a row of account cards based on the current accounts in the database."""
    accounts = AccountService().get_all_accounts()

    return AlphaRow(
        children=[
            AlphaCol(
                render_account_card(account),
                style={"marginBottom": "10px"},
                xs=12,
                sm=6,
                md=4,
                lg=4,
                xl=4,
            )
            for account in accounts
        ]
    )

def render_tv_calendar() -> html.Div:
    """Render the Trading View calendar."""
    return html.Div(
        children=[
            html.Iframe(
                srcDoc="""
                <!-- TradingView Widget BEGIN -->
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank"><span class="blue-text">Track all markets on TradingView</span></a></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
  {
  "colorTheme": "light",
  "isTransparent": false,
  "width": "400",
  "height": "550",
  "locale": "en",
  "importanceFilter": "0,1",
  "countryFilter": "ar,au,br,ca,cn,fr,de,in,id,it,jp,kr,mx,ru,sa,za,tr,gb,us,eu"
}
  </script>
</div>
<!-- TradingView Widget END -->
""",
                style={"height": "600px", "width": "100%", "border": "none"}
            )
        ]
    )

def render_bot_controls(bot_running: bool) -> html.Div:
    """Render the controls for the Discord bot, including start and stop buttons."""
    return html.Div(
        [
            AlphaRow(
                children=[
                    AlphaCol(
                        AlphaButton(
                            BOT_RUNNING_LABEL if bot_running else START_BOT_BTN_LABEL,
                            button_id=START_BOT_BTN_ID,
                            button_color=AlphaButtonColor.SUCCESS if bot_running else AlphaButtonColor.ERROR,
                        ).render(),
                        xs=12,
                        sm=6,
                        md=6,
                        lg=6,
                        xl=6,
                    ),
                    AlphaCol(
                        AlphaButton(
                            STOP_BOT_BTN_LABEL,
                            button_id=STOP_BOT_BTN_ID,
                            button_color=AlphaButtonColor.ERROR,
                            hidden=not bot_running,
                        ).render(),
                        xs=12,
                        sm=6,
                        md=6,
                        lg=6,
                        xl=6,
                    ),
                ]
            )
        ],
        style={"marginBottom": "20px"},
    )
