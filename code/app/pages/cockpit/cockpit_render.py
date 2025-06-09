from components.atoms.buttons.general.button import AlphaButton, AlphaButtonColor
from components.atoms.card.card import AlphaCard, AlphaCardBody, AlphaCardHeader
from components.atoms.layout.layout import AlphaCol, AlphaRow
from constants import colors
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


def render_account_cards() -> html.Div:
    """Render a list of account cards based on the current accounts in the database."""
    accounts = AccountService().get_all_accounts()

    return html.Div(
        children=[
            AlphaRow(
                children=[
                    AlphaCol(
                        children=render_account_card(account),
                        xs=12,
                        sm=6,
                        md=4,
                        lg=3,
                        xl=3,
                    )
                    for account in accounts
                ]
            )
        ]
    )


def render_account_management_row() -> html.Div:
    """Render a row of account cards based on the current accounts in the database."""

    return html.Div(
        children=[
            AlphaRow(
                children=[
                    AlphaCard(
                        header=AlphaCardHeader(
                            children=[
                                html.H3("Account Management", style={"textAlign": "center"}),
                                html.P(
                                    "Click on an account to toggle its enabled state.",
                                    style={"textAlign": "center", "color": colors.TEXT_DISABLED},
                                ),
                            ]
                        ).render(),
                        body=AlphaCardBody(
                            children=[
                                html.Div(id="account-toggle-container", children=render_account_cards()),
                            ]
                        ).render(),
                        show_divider=True,
                        style={
                            "backgroundColor": "#ffffff",
                            "marginBottom": "20px",
                        },
                    ).render()
                ]
            )
        ]
    )


def _render_tv_calendar() -> html.Div:
    """Render the Trading View calendar."""
    return html.Div(
        children=[
            html.Iframe(
                srcDoc="""
                <!-- TradingView Widget BEGIN -->
                    <div class="tradingview-widget-container">
                      <div class="tradingview-widget-container__widget"></div>
                      <div
                      class="tradingview-widget-copyright"><a href="https://www.tradingview.com/"
                          rel="noopener nofollow"
                          target="_blank"
                      >
                      <span class="blue-text">
                        Track all markets on TradingView
                      </span></a></div>
                      <script
                        type="text/javascript"
                        src="https://s3.tradingview.com/external-embedding/embed-widget-events.js"
                        async>
                      {
                      "colorTheme": "light",
                      "isTransparent": false,
                      "width": "100%",
                      "height": "600px",
                      "locale": "en",
                      "importanceFilter": "0,1",
                      "countryFilter": "ar,au,br,ca,cn,fr,de,in,id,it,jp,kr,mx,ru,sa,za,tr,gb,us,eu"
                    }
                      </script>
                    </div>
                    <!-- TradingView Widget END -->
                    """,
                style={"height": "600px", "width": "100%", "border": "none"},
            )
        ]
    )


def render_tv_calendar_row() -> html.Div:
    """Render a card containing the Trading View calendar widget."""
    return html.Div(
        children=[
            AlphaCard(
                header=AlphaCardHeader(
                    children=[
                        html.H3("Trading View Calendar", style={"textAlign": "center"}),
                    ]
                ).render(),
                body=AlphaCardBody(
                    children=[
                        AlphaRow(
                            children=[
                                AlphaCol(
                                    children=[_render_tv_calendar()],
                                    xs=12,
                                    sm=12,
                                    md=12,
                                    lg=6,
                                    xl=6,
                                )
                            ]
                        )
                    ],
                ).render(),
                show_divider=True,
                style={
                    "backgroundColor": "#ffffff",
                },
            ).render()
        ],
    )


def render_bot_controls_row(bot_running: bool) -> html.Div:
    """Render the controls for the Discord bot, including start and stop buttons."""
    return html.Div(
        children=[
            AlphaCard(
                header=AlphaCardHeader(
                    children=[
                        html.H3("Discord Bot Controls", style={"textAlign": "center"}),
                        html.P(
                            "Start or stop the trading signal bot. Only one bot should run at a time.",
                            style={"textAlign": "center", "color": colors.TEXT_DISABLED},
                        ),
                    ]
                ).render(),
                body=AlphaCardBody(
                    children=[
                        AlphaRow(
                            children=[
                                AlphaCol(
                                    AlphaButton(
                                        BOT_RUNNING_LABEL if bot_running else START_BOT_BTN_LABEL,
                                        button_id=START_BOT_BTN_ID,
                                        button_color=(
                                            AlphaButtonColor.SUCCESS if bot_running else AlphaButtonColor.ERROR
                                        ),
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
                    ]
                ).render(),
                show_divider=True,
                style={
                    "backgroundColor": "#ffffff",
                    "marginBottom": "20px",
                },
            ).render()
        ]
    )
