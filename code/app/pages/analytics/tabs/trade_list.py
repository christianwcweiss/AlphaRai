from dash import html


def render(df):
    return html.Div(
        [
            html.H4("Trade List Coming Soon"),
            # your charts using df go here
        ]
    )
