from typing import Tuple, List, Dict, Any

import dash
from dash import dcc, html

from components.atoms.content import MainContent
from components.atoms.tabbar.tabbar import AlphaTabToolbar
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from components.molecules.toolbars.analytics_toolbar import AnalyticsToolbarMolecule
from pages.analytics.analysis import TAB_LABELS
from pages.base_page import BasePage

from pages.analytics.overview.overview_callbacks import render_overview_content  # type: ignore[import]

dash.register_page(__name__, path="/analytics/overview", name="Overview")


class AnalysisOverviewPage(BasePage):
    """Overview Page for Analytics."""

    def render(self):
        return PageBody(
            [
                PageHeader(self._title).render(),
                MainContent(
                    [
                        AlphaTabToolbar(
                            tab_labels=TAB_LABELS,
                            base_href="/analytics",
                            current_tab="overview",
                            link_with_hash=False,
                        ).render(),
                        AnalyticsToolbarMolecule().render(),
                        dcc.Loading(html.Div(id="overview-content")),
                    ]
                ),
            ]
        )


layout = AnalysisOverviewPage("Overview").layout
