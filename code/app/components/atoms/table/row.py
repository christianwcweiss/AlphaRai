from typing import Optional, Union, List

from dash.development.base_component import Component
import dash_bootstrap_components as dbc


class AlphaRow(dbc.Row):
    def __init__(
        self, children: List[Component], id: Optional[Union[str, dict]] = None, class_name: str = "", **kwargs
    ) -> None:
        # Remove any incoming className to prevent duplication
        kwargs.pop("className", None)

        full_class = f"mb-3 p-3 rounded border {class_name}".strip()
        super().__init__(children=children, id=id, className=full_class, **kwargs)
