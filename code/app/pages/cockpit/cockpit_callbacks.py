from dash import Input, Output, callback, callback_context
from quant_core.services.core_logger import CoreLogger
from services.relay_bot import DiscordRelayBot


@callback(
    Output("download-signals-status", "children"), Input("download-signals-btn", "n_clicks"), prevent_initial_call=True
)
def download_signals(n_clicks):
    ctx = callback_context
    if not ctx.triggered_id or n_clicks is None:
        return ""

    try:
        DiscordRelayBot().download_all_messages()
        return "✅ Signals downloaded successfully."
    except Exception as e:
        CoreLogger().error(f"Signal download failed: {e}")
        return "❌ Download failed. Check logs."
