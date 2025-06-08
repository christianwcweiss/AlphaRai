from typing import List

import dash
import dash_bootstrap_components as dbc
from components.atoms.buttons.general.button import AlphaButton
from components.atoms.content import MainContent
from components.atoms.divider.divider import Divider
from components.atoms.layout.layout import AlphaCol, AlphaRow
from components.atoms.modal.modal import AlphaModal
from components.atoms.table.table import AlphaTable
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from dash import Input, Output, State, callback, ctx, html
from pages.base_page import BasePage
from quant_core.confluences.confluences import CONFLUENCE_LIST
from quant_core.enums.time_period import TimePeriod
from services.db.main.confluence import delete_confluence, get_all_confluences, get_confluence_by_id, upsert_confluence

dash.register_page(__name__, path="/confluences", name="Confluences")


def _confluence_modal_fields(prefix: str, confluence_id="", period="", weight=100):
    return html.Div(
        [
            dbc.Select(
                id=f"{prefix}-id",
                value=confluence_id,
                placeholder="Select Confluence",
                options=sorted(
                    [
                        {"label": cls.__NAME__, "value": getattr(cls, "__SLUG__", cls.__name__)}
                        for cls in CONFLUENCE_LIST
                    ],
                    key=lambda x: x["label"],
                ),
                className="mb-2",
                disabled=(prefix == "modal-edit"),
            ),
            dbc.Select(
                id=f"{prefix}-period",
                value=period,
                className="mb-2",
                options=[{"label": p.name, "value": p.value} for p in TimePeriod],
            ),
            dbc.Input(
                id=f"{prefix}-weight", value=weight, type="number", placeholder="Weight (0-100)", className="mb-2"
            ),
        ]
    )


def build_confluence_table() -> html.Table:
    """Build the confluence settings table."""
    confluences = get_all_confluences()
    headers = ["ID", "Time Period", "Weight", "Enabled", "Actions"]
    rows = []

    for conf in confluences:
        actions = AlphaRow(
            [
                AlphaCol(
                    AlphaButton(
                        "✏️",
                        {"type": "edit-confluence", "index": conf.confluence_id},
                    ).render(),
                    width="auto",
                )
            ]
        )

        actions.children.append(
            AlphaCol(
                AlphaButton(
                    "🗑️",
                    {"type": "delete-confluence", "index": conf.confluence_id},
                ).render(),
                width="auto",
            )
        )

        rows.append([conf.confluence_id, conf.period.name, conf.weight, "✅" if conf.enabled else "❌", actions])

    return AlphaTable(table_id="confluence-settings-table", headers=headers, rows=rows).render()


class ConfluencesPage(BasePage):
    """Confluences Page."""

    def render(self) -> html.Div:
        return PageBody(
            [
                PageHeader("Confluences").render(),
                MainContent(
                    [
                        # build_confluence_table(),
                        Divider().render(),
                        AlphaButton("➕ Add Confluence", "open-add-confluence-btn").render(),
                        AlphaModal(
                            modal_id="add-confluence-modal",
                            title="Add Confluence",
                            body_content=_confluence_modal_fields("modal-add"),
                            confirm_id="confirm-add-confluence",
                            cancel_id="cancel-add-confluence",
                        ).render(),
                        AlphaModal(
                            modal_id="edit-confluence-modal",
                            title="Edit Confluence",
                            body_content=_confluence_modal_fields("modal-edit"),
                            confirm_id="confirm-edit-confluence",
                            cancel_id="cancel-edit-confluence",
                        ).render(),
                    ]
                ),
            ]
        )


page = ConfluencesPage("Confluences")
layout = page.layout


@callback(
    Output("add-confluence-modal", "is_open"),
    [
        Input("open-add-confluence-btn", "n_clicks"),
        Input("confirm-add-confluence", "n_clicks"),
        Input("cancel-add-confluence", "n_clicks"),
    ],
    State("add-confluence-modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_add_modal(_, __, ___, ____) -> bool:
    """Toggle the add confluence modal."""
    return ctx.triggered_id == "open-add-confluence-btn"


@callback(
    Output("edit-confluence-modal", "is_open"),
    Output("modal-edit-id", "value"),
    Output("modal-edit-period", "value"),
    Output("modal-edit-weight", "value"),
    Input({"type": "edit-confluence", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def open_edit_modal(edit_clicks: List[int]) -> tuple[bool, str, int, int]:
    """Open the edit confluence modal."""
    if not any(edit_clicks):
        raise dash.exceptions.PreventUpdate

    triggered = ctx.triggered_id
    confluence_id = triggered.get("index")
    conf = get_confluence_by_id(confluence_id)

    if not conf:
        raise dash.exceptions.PreventUpdate

    return True, conf.confluence_id, conf.period.value, conf.weight


@callback(
    Output("confluence-settings-table", "children", allow_duplicate=True),
    Input("confirm-add-confluence", "n_clicks"),
    State("modal-add-id", "value"),
    State("modal-add-period", "value"),
    State("modal-add-weight", "value"),
    prevent_initial_call=True,
)
def save_new_confluence(_, confluence_id: str, period: int, weight: int) -> html.Table:
    """Save the new confluence."""
    if not confluence_id or not period:
        raise dash.exceptions.PreventUpdate

    upsert_confluence(confluence_id, TimePeriod(int(period)), weight)
    return build_confluence_table()


@callback(
    Output("confluence-settings-table", "children", allow_duplicate=True),
    Input("confirm-edit-confluence", "n_clicks"),
    State("modal-edit-id", "value"),
    State("modal-edit-period", "value"),
    State("modal-edit-weight", "value"),
    prevent_initial_call=True,
)
def save_edited_confluence(_, confluence_id: str, period: int, weight: int) -> html.Table:
    """Save the edited confluence."""
    if not confluence_id or not period:
        raise dash.exceptions.PreventUpdate

    upsert_confluence(confluence_id, TimePeriod(period), weight)

    return build_confluence_table()


@callback(
    Output("confluence-settings-table", "children", allow_duplicate=True),
    Input({"type": "delete-confluence", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def delete_selected_confluence(_) -> html.Table:
    """Delete the selected confluence."""
    triggered = ctx.triggered_id
    confluence_id = triggered.get("index")
    delete_confluence(confluence_id)

    return build_confluence_table()
