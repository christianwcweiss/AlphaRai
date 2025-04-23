import random
import string
from typing import Optional

import dash
import dash_bootstrap_components as dbc
from dash import html, Input, Output, ALL, callback, ctx, State, dcc

from components.atoms.card.card import AlphaCard
from components.atoms.content import MainContent
from components.atoms.text.page import PageHeader
from components.atoms.text.section import SectionHeader
from components.atoms.table.row import AlphaRow
from components.atoms.table.table import AlphaTable
from components.frame.body import PageBody
from pages.base_page import BasePage
from quant_core.enums.platform import Platform
from services.accounts import (
    get_all_accounts,
    upsert_account,
    delete_account,
)

dash.register_page(__name__, path="/settings", name="Settings")


class SettingsPage(BasePage):
    def render(self):
        return PageBody(
            [
                html.Div(id="page-init", style={"display": "none"}),  # Triggers page load
                PageHeader("Settings"),
                MainContent(
                    [
                        AlphaCard(
                            title="Accounts", href="/settings/accounts", children=[], aspect_ratio="1", height="200px"
                        ),
                    ]
                ),
            ]
        )


page = SettingsPage("Settings")
layout = page.layout
