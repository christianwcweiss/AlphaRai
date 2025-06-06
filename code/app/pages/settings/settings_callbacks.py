import dash_bootstrap_components as dbc
from dash import Input, Output, callback
from dash.exceptions import PreventUpdate
from pages.settings.settings_contants import (
    POLYGON_API_KEY_INPUT_ID,
    TRADE_WINDOW_END,
    TRADE_WINDOW_START,
    TRADE_WINDOW_START_HOUR_ID,
    TRADE_WINDOW_START_MINUTE_ID,
    TRADE_WINDOW_START_WEEKDAY_ID,
    TRADE_WINDOW_STOP_HOUR_ID,
    TRADE_WINDOW_STOP_MINUTE_ID,
    TRADE_WINDOW_STOP_WEEKDAY_ID,
)
from quant_core.enums.weekday import Weekday
from quant_core.services.core_logger import CoreLogger
from quant_core.utils.time_utils import (
    convert_minutes_since_week_started_to_time,
    convert_time_data_to_minutes_since_week_started,
)
from services.db.cache.trade_history import sync_trades_from_all_accounts
from services.db.main.general_setting import GeneralSettingService


@callback(
    Output(TRADE_WINDOW_START_WEEKDAY_ID, "value"),
    Output(TRADE_WINDOW_START_HOUR_ID, "value"),
    Output(TRADE_WINDOW_START_MINUTE_ID, "value"),
    Output(TRADE_WINDOW_STOP_WEEKDAY_ID, "value"),
    Output(TRADE_WINDOW_STOP_HOUR_ID, "value"),
    Output(TRADE_WINDOW_STOP_MINUTE_ID, "value"),
    Input("url", "pathname"),
)
def load_trade_window_settings(_):
    """Load the trade window settings from the database and return them in a format suitable for the UI."""
    start_setting = GeneralSettingService.get_setting_by_key(TRADE_WINDOW_START)
    stop_setting = GeneralSettingService.get_setting_by_key(TRADE_WINDOW_END)

    start_min = int(start_setting.value) if start_setting else 180
    stop_min = int(stop_setting.value) if stop_setting else 7020

    start_day, start_hour, start_minute = convert_minutes_since_week_started_to_time(start_min)
    stop_day, stop_hour, stop_minute = convert_minutes_since_week_started_to_time(stop_min)

    return (start_day.name, str(start_hour), f"{start_minute:02}", stop_day.name, str(stop_hour), f"{stop_minute:02}")


@callback(
    Output("trade-window-store", "data", allow_duplicate=True),
    Input(TRADE_WINDOW_START_WEEKDAY_ID, "value"),
    Input(TRADE_WINDOW_START_HOUR_ID, "value"),
    Input(TRADE_WINDOW_START_MINUTE_ID, "value"),
    Input(TRADE_WINDOW_STOP_WEEKDAY_ID, "value"),
    Input(TRADE_WINDOW_STOP_HOUR_ID, "value"),
    Input(TRADE_WINDOW_STOP_MINUTE_ID, "value"),
    prevent_initial_call=True,
)
def save_trade_window_settings(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    start_day: str, start_hour: str, start_min: str, stop_day: str, stop_hour: str, stop_min: str
) -> str:
    """Save the trade window settings to the database."""
    try:
        start_minutes = convert_time_data_to_minutes_since_week_started(
            Weekday[start_day], int(start_hour), int(start_min)
        )
        stop_minutes = convert_time_data_to_minutes_since_week_started(Weekday[stop_day], int(stop_hour), int(stop_min))

        GeneralSettingService.upsert_setting(TRADE_WINDOW_START, str(start_minutes))
        GeneralSettingService.upsert_setting(TRADE_WINDOW_END, str(stop_minutes))

        return ""
    except Exception as exception:  # pylint: disable=broad-exception-caught
        return f"Error saving trade window: {str(exception)}"


@callback(
    Output(POLYGON_API_KEY_INPUT_ID, "value"),
    Input("url", "pathname"),
)
def load_polygon_api_key(_: str):
    """Load the Polygon API key from the database and return it masked."""
    setting = GeneralSettingService.get_setting_by_key("POLYGON_API_KEY")

    return "*" * len(setting.value) if setting and setting.value else ""


@callback(Output("polygon-api-key-store", "data"), Input(POLYGON_API_KEY_INPUT_ID, "value"), prevent_initial_call=True)
def save_polygon_api_key(value) -> str:
    """Save the Polygon API key to the database."""
    if not value or value == "*****":
        raise PreventUpdate

    try:
        GeneralSettingService.upsert_setting("POLYGON_API_KEY", value)
        return "*****"
    except Exception:  # pylint: disable=broad-exception-caught
        return ""


@callback(
    Output("sync-trades-status", "children"),
    Input("sync-trades-btn", "n_clicks"),
    prevent_initial_call=True,
)
def sync_trades_from_metatrader_5(_) -> dbc.Alert:
    """Sync Trades from MetaTrader 5 and store them in the database."""
    try:
        result = sync_trades_from_all_accounts()
        CoreLogger().info("Successfully synced trades from MetaTrader.")
        return dbc.Alert(f"✅ Synced trades: {result}", color="success", dismissable=True)
    except Exception as error:  # pylint: disable=broad-exception-caught
        CoreLogger().error(f"During sync trades from MetaTrader the following error occured: {str(error)}")
        return dbc.Alert(f"❌ Sync failed: {str(error)}", color="danger", dismissable=True)
