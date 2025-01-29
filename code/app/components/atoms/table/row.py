from typing import List, Optional, Union

import dash_bootstrap_components as dbc
from dash.development.base_component import Component


class AlphaRow(dbc.Row):
    def __init__(
        self,
        children: List[Component],
        id: Optional[Union[str, dict]] = None,
        class_name: str = "",
        **kwargs
    ) -> None:
        """
        A reusable, styled Bootstrap row with sensible defaults.

        Args:
            children: List of Dash components inside the row.
            id: Optional Dash `id` (str or dict for pattern-matching).
            class_name: Additional Bootstrap classNames.
            **kwargs: Additional props passed to dbc.Row.
        """
        full_class = f"mb-3 p-3 rounded border {class_name}".strip()
        super().__init__(
            children=children,
            id=id,
            className=full_class,
            **kwargs
        )
