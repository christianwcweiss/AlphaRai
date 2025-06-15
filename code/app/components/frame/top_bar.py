import dash_bootstrap_components as dbc
from components.molecules.banners.bot_status.banner import BotStatusBanner
from constants.colors import PRIMARY_COLOR
from dash import html
from dash.development.base_component import Component

APP_BAR_ITEMS = [
    {"name": "Cockpit", "path": "/"},
    {"name": "Analytics", "path": "/analytics/overview"},
    {"name": "Accounts", "path": "/accounts"},
    {"name": "Settings", "path": "/settings"},
]


class TopBar(dbc.NavbarSimple):  # pylint: disable=too-few-public-methods
    """A top bar component for Dash applications."""

    def __init__(self, bot_status_component: Component):
        super().__init__(
            brand="AlphaRai",
            color=PRIMARY_COLOR,
            children=[dbc.NavItem(dbc.NavLink(item["name"], href=item["path"])) for item in APP_BAR_ITEMS]
            + [
                html.Div(
                    style={
                        "borderLeft": "1px solid white",
                        "height": "30px",
                        "margin": "auto 1rem",
                    }
                ),
                dbc.NavItem(
                    children=[
                        html.Div(
                            id="topbar-bot-status",
                            children=html.Div(
                                id="bot-status-banner-container",
                                children=BotStatusBanner(is_running=False).render(),
                                className="d-flex align-items-center gap-2",
                                style={"height": "100%"},
                            ),
                        ),
                    ]
                ),
                html.Div(
                    style={
                        "borderLeft": "1px solid white",
                        "height": "30px",
                        "margin": "auto 1rem",
                    }
                ),
                dbc.NavItem(
                    children=html.Div(
                        id="topbar-account-control",
                        className="d-flex align-items-center gap-2 text-white",
                        children=[
                            html.Div(id="topbar-enabled-accounts", children="Enabled Accounts: 0"),
                            dbc.DropdownMenu(
                                id="topbar-account-dropdown",
                                label="Manage",
                                color="secondary",
                                children=[],
                                toggle_style={"background": "white", "color": "#333"},
                                style={"margin": "20px", "borderRadius": "10px", "overflow": "visible", "zIndex": 1000},
                            ),
                        ],
                    )
                ),
            ],
            style={"margin": "20px", "borderRadius": "10px", "overflow": "hidden"},
        )
