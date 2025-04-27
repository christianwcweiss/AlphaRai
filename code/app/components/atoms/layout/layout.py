
import dash_bootstrap_components as dbc


class AlphaRow(dbc.Row):
    def __init__(self, *args, **kwargs):
        class_name = kwargs.pop("className", "")
        super().__init__(*args, className=f"{class_name} my-2", **kwargs)

class AlphaCol(dbc.Col):
    def __init__(self, *args, **kwargs):
        class_name = kwargs.pop("className", "")
        super().__init__(*args, className=f"{class_name} px-2", **kwargs)
