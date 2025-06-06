import dash
from components.atoms.content import MainContent
from components.atoms.tabbar.tabbar import AlphaTabToolbar
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from dash import dcc, html
from pages.analytics.analysis import TAB_LABELS
from pages.base_page import BasePage

dash.register_page(__name__, path="/analytics/behavior", name="Behavior")


class BehaviorPage(BasePage):
    """Behavior Page."""

    def render(self):
        return PageBody(
            [
                PageHeader(self._title).render(),
                MainContent(
                    [
                        AlphaTabToolbar(
                            tab_labels=TAB_LABELS,
                            base_href="/analytics",
                            current_tab="behavior",
                            link_with_hash=False,
                        ).render(),
                        dcc.Loading(html.Div(id="behavior-content")),
                    ]
                ),
            ]
        )


layout = BehaviorPage("Behavior").layout
