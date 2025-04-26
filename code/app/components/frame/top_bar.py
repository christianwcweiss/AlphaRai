import dash_bootstrap_components as dbc

from constants.colors import PRIMARY_COLOR

APP_BAR_ITEMS = [
    {"name": "Cockpit", "path": "/"},
    {"name": "Analysis", "path": "/analysis"},
    {"name": "Settings", "path": "/settings"},
]


class TopBar(dbc.NavbarSimple):
    def __init__(self):
        super().__init__(
            brand="AlphaRai",
            color=PRIMARY_COLOR,
            children=[dbc.NavItem(dbc.NavLink(item["name"], href=item["path"])) for item in APP_BAR_ITEMS],
            style={"margin": "20px", "borderRadius": "10px", "overflow": "hidden"},
        )
