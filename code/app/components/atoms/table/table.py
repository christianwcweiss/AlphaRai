from typing import List, Tuple, Optional, Union

import dash_bootstrap_components as dbc
from dash import html
from dash.development.base_component import Component

from components.atoms.table.row import AlphaRow


class AlphaTable(html.Div):
    def __init__(
        self,
        table_id: str,
        header_row: AlphaRow,
        rows: List[AlphaRow],
        class_name: str = "",
    ) -> None:
        """
        A styled table-like layout using Dash Bootstrap Rows and Columns.
        """
        super().__init__(
            id=table_id, className=f"styled-table bg-white p-3 rounded {class_name}", children=[header_row, *rows]
        )
