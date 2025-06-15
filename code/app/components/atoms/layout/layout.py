import dash_bootstrap_components as dbc


class AlphaRow(dbc.Row):  # pylint: disable=too-few-public-methods
    """A row component for Dash applications."""

    def __init__(self, *args, **kwargs) -> None:
        class_name = kwargs.pop("className", "")
        super().__init__(*args, className=f"{class_name} my-2", **kwargs)


class AlphaCol(dbc.Col):  # pylint: disable=too-few-public-methods
    """A column component for Dash applications."""

    def __init__(self, *args, **kwargs) -> None:
        class_name = kwargs.pop("className", "")
        super().__init__(*args, className=f"{class_name} px-2", style={"padding": "5px"}, **kwargs)
