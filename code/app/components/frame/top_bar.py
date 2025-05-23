import dash_bootstrap_components as dbc

from constants.colors import PRIMARY_COLOR

APP_BAR_ITEMS = [
    {"name": "Cockpit", "path": "/"},
    {"name": "Analytics", "path": "/analytics/overview"},
    {"name": "Accounts", "path": "/accounts"},
    {"name": "Settings", "path": "/settings"},
]


class TopBar(dbc.NavbarSimple):  # pylint: disable=too-few-public-methods
    """A top bar component for Dash applications."""

    def __init__(self):
        super().__init__(
            brand="AlphaRai",
            color=PRIMARY_COLOR,
            children=[dbc.NavItem(dbc.NavLink(item["name"], href=item["path"])) for item in APP_BAR_ITEMS],
            style={"margin": "20px", "borderRadius": "10px", "overflow": "hidden"},
        )
