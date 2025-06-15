# signal_timeline.py

from dash import html
from services.db.cache.signals import SignalService


def render_signal_timeline() -> html.Div:
    signals = SignalService().get_all_signals()

    sorted_signals = sorted(signals, key=lambda signal: signal.created_at)

    return html.Div(
        children=[
            html.Div(
                className="signal-timeline-entry",
                children=[
                    html.Span(f"{signal.direction} {signal.symbol}", className="signal-direction"),
                    html.Div(
                        f"Entry: {signal.entry} | SL: {signal.stop_loss} | TP1: {signal.take_profit_1}",
                        className="signal-details",
                    ),
                    html.Small(signal.created_at),
                ],
                style={"borderBottom": "1px solid #ccc", "padding": "10px"},
            )
            for signal in sorted_signals
        ],
        style={"display": "flex", "flexDirection": "column-reverse"},  # newest on top
    )
