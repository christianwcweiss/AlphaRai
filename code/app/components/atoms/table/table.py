from typing import Any, Dict, List, Optional, Union

from components.atoms.atom import Atom
from dash import html
from dash.development.base_component import Component


class AlphaTableCell(Atom):
    """A cell in the table."""

    DEFAULT_CELL_STYLE = {
        "border": "1px solid #ccc",
        "textAlign": "center",
        "padding": "8px",
    }

    def __init__(self, content: Union[str, Component], is_header: bool = False):
        self._content = content
        self._is_header = is_header
        self.validate()

    def validate(self) -> None:
        if self._content is None:
            raise ValueError("Cell content cannot be None.")

    def render(self) -> Component:
        if self._is_header:
            return html.Th(self._content, style=self.DEFAULT_CELL_STYLE)

        return html.Td(self._content, style=self.DEFAULT_CELL_STYLE)


class AlphaTableRow(Atom):
    """A row in the table."""

    def __init__(self, cells: List[AlphaTableCell]):
        self._cells = cells
        self.validate()

    def validate(self) -> None:
        """Validate the row."""
        if not self._cells:
            raise ValueError("Row must have at least one cell.")

    def render(self) -> Component:
        return html.Tr([cell.render() for cell in self._cells])


class AlphaTable(Atom):  # pylint: disable=too-few-public-methods
    """A table component for Dash applications."""

    DEFAULT_STYLE = {
        "width": "100%",
        "borderCollapse": "collapse",
        "textAlign": "center",
        "border": "1px solid #ccc",
    }

    def __init__(
        self,
        headers: List[str],
        rows: List[List[Union[str, Component]]],
        table_id: Optional[str] = None,
        style: Optional[Dict[str, Any]] = None,
    ):
        self._headers = headers
        self._raw_rows = rows
        self._id = table_id
        self._style = {**self.DEFAULT_STYLE, **(style or {})}

        self.validate()

    def validate(self) -> None:
        if not self._headers:
            raise ValueError("Headers cannot be empty.")

    def render(self) -> html.Table:
        header_row = AlphaTableRow(cells=[AlphaTableCell(content=h, is_header=True) for h in self._headers]).render()

        body_rows = [
            AlphaTableRow(cells=[AlphaTableCell(content=cell) for cell in row]).render() for row in self._raw_rows
        ]

        return html.Table(id=self._id, style=self._style, children=[html.Thead(header_row), html.Tbody(body_rows)])
