import json
from http import HTTPStatus
from typing import Any, Dict, Tuple

from quant_core.bodies.trading_view import TradingViewAlertBody
from quant_core.features.indicators.average_true_range import DataFeatureAverageTrueRange
from quant_core.clients.aws.sns import SNSClient
from quant_core.clients.polygon_client.poly_client import PolygonClient
from quant_core.entities.response import Response
from quant_core.enums.asset_type import AssetType
from quant_core.enums.discord_channels import DiscordChannel
from quant_core.enums.time_period import TimePeriod
from quant_core.enums.trade_direction import TradeDirection
from quant_core.services.core_logger import CoreLogger
from quant_core.services.discord_bot import DiscordBot
from quant_core.settings.configuration import Configuration


def _get_entry_and_exit_prices(alert: TradingViewAlertBody) -> Tuple[float, float, float, float, float]:
    """Extracts the entry price from the parsed body."""
    polygon_client = PolygonClient()
    symbol = alert.symbol

    if alert.asset_type is AssetType.CRYPTO:
        data_frame = polygon_client.get_crypto_data(symbol=symbol, time_period=alert.period, n_candles=2000)
    elif alert.asset_type is AssetType.STOCK:
        data_frame = polygon_client.get_stock_data(symbol=symbol, time_period=alert.period, n_candles=2000)
    elif alert.asset_type is AssetType.FOREX:
        data_frame = polygon_client.get_forex_data(symbol=symbol, time_period=alert.period, n_candles=2000)
    elif alert.asset_type is AssetType.INDICES:
        raise NotImplementedError("Indices data retrieval is not implemented yet.")
    else:
        raise ValueError(f"Unsupported asset type: {alert.asset_type}")

    atr_14_feature = DataFeatureAverageTrueRange(atr_period=14)

    data_frame = atr_14_feature.add_feature(data_frame)

    if alert.direction.normalize() is TradeDirection.LONG:
        entry_price = data_frame.iloc[-1]["close"]
        stop_loss_price = entry_price - data_frame.iloc[-1]["atr_14"] * 2
        take_profit_1_price = entry_price + (data_frame.iloc[-1]["atr_14"])
        take_profit_2_price = entry_price + (data_frame.iloc[-1]["atr_14"] * 2)
        take_profit_3_price = entry_price + (data_frame.iloc[-1]["atr_14"] * 3)
    else:
        entry_price = data_frame.iloc[-1]["close"]
        stop_loss_price = entry_price + data_frame.iloc[-1]["atr_14"] * 2
        take_profit_1_price = entry_price - (data_frame.iloc[-1]["atr_14"])
        take_profit_2_price = entry_price - (data_frame.iloc[-1]["atr_14"] * 2)
        take_profit_3_price = entry_price - (data_frame.iloc[-1]["atr_14"] * 3)

    return entry_price, stop_loss_price, take_profit_1_price, take_profit_2_price, take_profit_3_price


def _build_message(parsed_body: TradingViewAlertBody) -> Tuple[str, str]:
    """Builds a message from the parsed body."""
    headline = f"{parsed_body.direction.normalize().value.upper()} {parsed_body.symbol.upper()}\n\n"
    symbol = f"Symbol = {parsed_body.symbol}\n"
    direction = f"Direction = {parsed_body.direction.value}\n"
    timeframe = f"Timeframe = {parsed_body.period.value}\n"

    entry_price, stop_loss_price, take_profit_1_price, take_profit_2_price, take_profit_3_price = (
        _get_entry_and_exit_prices(parsed_body)
    )

    entry = f"Entry = {round(entry_price, 5)}\n"
    stop_loss = f"Stop Loss = {round(stop_loss_price, 5)}\n"
    take_profit_1 = f"Take Profit 1 = {round(take_profit_1_price, 5)}\n"
    take_profit_2 = f"Take Profit 2 = {round(take_profit_2_price, 5)}\n"
    take_profit_3 = f"Take Profit 3 = {round(take_profit_3_price, 5)}\n"

    return headline, symbol + direction + timeframe + entry + stop_loss + take_profit_1 + take_profit_2 + take_profit_3


def handle(event: Dict[str, Any], _: Dict[str, Any]) -> Dict[str, Any]:
    """Forward request to the correct lambda function based on the event."""

    # Example Payload:
    # {
    #     "body": "{
    #         \"symbol\":\"LINKUSD\",
    #         \"period\":\"15\",
    #         \"direction\":\"BUY\",
    #         \"assetType\":\"CRYPTO\",
    #         \"time\":\"2025-05-01T14:30:00Z\",
    #         \"poweredBy\":\"TradingView\"
    #     }"
    # }

    event_body = json.loads(event.get("body", "{}"))
    CoreLogger().info(f"Received event body: {json.dumps(event_body, indent=2)}")

    parsed_body = TradingViewAlertBody(
        symbol=event_body["symbol"],
        direction=TradeDirection(event_body["direction"]),
        period=TimePeriod(int(event_body["period"])),
        asset_type=AssetType(event_body["assetType"]),
        time=event_body["time"],
        powered_by=event_body.get("poweredBy"),
    )

    CoreLogger().info(f"Building message from parsed body: {parsed_body.to_dict()}")
    headline, trade_message = _build_message(parsed_body)

    if parsed_body.asset_type is AssetType.CRYPTO:
        discord_channel = DiscordChannel.CRYPTO_SIGNALS
    elif parsed_body.asset_type is AssetType.FOREX:
        discord_channel = DiscordChannel.FOREX_SIGNALS
    elif parsed_body.asset_type is AssetType.STOCK:
        discord_channel = DiscordChannel.STOCK_SIGNALS
    elif parsed_body.asset_type is AssetType.INDICES:
        discord_channel = DiscordChannel.INDICES_SIGNALS
    else:
        raise NotImplementedError(f"Unsupported asset type: {parsed_body.asset_type}")

    CoreLogger().info(f"Trade message: {trade_message}")

    CoreLogger().info(f"Publishing to SNS: {Configuration().sns_topic_arn}")
    SNSClient().publish(topic_arn=Configuration().sns_topic_arn, message=parsed_body.to_sns_body())

    CoreLogger().info(f"Publishing event to Discord: {discord_channel.value}")
    DiscordBot().send(title=headline, message=trade_message, discord_channel=discord_channel)

    return Response(HTTPStatus.OK, "Signal has been successfully published to SNS!").to_response()
