import re
from contextlib import suppress

from entities.trade_details import TradeDetails
from quant_core.services.core_logger import CoreLogger


class TradeMessageParser:
    """Parser for trade messages from Algopro and Alpharai chat."""

    @staticmethod
    def parse_algopro_chat(message: str) -> TradeDetails:
        """Parse a trade message from Algopro chat."""
        lines = message.strip().splitlines()
        symbol = lines[0].strip()

        match = re.search(r"(Buy|Sell)\s+Signal\s+on\s+(\d+)\s+(\w+)\s+timeframe", lines[1], re.IGNORECASE)
        if not match:
            raise ValueError("Invalid signal format in line 2")

        direction = match.group(1).upper()
        timeframe = match.group(2)

        data = {}
        for line in lines[2:]:
            if ":" not in line:
                continue
            key, value = map(str.strip, line.split(":", 1))
            try:
                value = float(value.replace("%", ""))  # type: ignore
            except ValueError:
                continue
            data[key] = value

        if "Take Profit 1" not in data:
            raise ValueError("Missing required field: Take Profit 1")

        return TradeDetails(
            symbol=symbol,
            direction=direction,
            timeframe=timeframe,
            entry=data.get("Entry"),
            stop_loss=data.get("Stop Loss"),
            take_profit_1=data.get("Take Profit 1"),
            take_profit_2=data.get("Take Profit 2"),
            take_profit_3=data.get("Take Profit 3"),
            ai_confidence=data.get("AI Confidence"),
        )

    @staticmethod
    def parse_alpharai_chat(message: str) -> TradeDetails:
        """Parse a trade message from Alpharai chat."""
        CoreLogger().info(f"Received Alpharai chat message: {message}")
        lines = message.strip().splitlines()
        lines.pop(0)

        symbol = lines[0].split("=")[1].strip()
        direction = lines[1].split("=")[1].strip()

        timeframe = lines[2].split("=")[1].strip()

        data = {}
        for line in lines[3:]:
            if "=" not in line:
                continue
            key, value = map(str.strip, line.split("=", 1))
            try:
                value = float(value)  # type: ignore
            except ValueError:
                continue
            data[key] = value

        if "Entry" not in data:
            raise ValueError("Missing required field: Entry")

        if "Take Profit 1" not in data:
            raise ValueError("Missing required field: Take Profit 1")

        return TradeDetails(
            symbol=symbol,
            direction=direction,
            timeframe=timeframe,
            entry=data.get("Entry"),
            stop_loss=data.get("Stop Loss"),
            take_profit_1=data.get("Take Profit 1"),
            take_profit_2=data.get("Take Profit 2"),
            take_profit_3=data.get("Take Profit 3"),
        )

    @staticmethod
    def parse(message: str) -> TradeDetails:
        """Parse a trade message from Algopro or Alpharai chat."""
        parsed_trade = None

        with suppress(ValueError):
            parsed_trade = TradeMessageParser.parse_algopro_chat(message)
        if not parsed_trade:
            with suppress(ValueError):
                parsed_trade = TradeMessageParser.parse_alpharai_chat(message)

        if parsed_trade is None:
            raise ValueError("Failed to parse trade message from Algopro or Alpharai chat")

        CoreLogger().info(f"Parsed trade: {parsed_trade}")
        return parsed_trade
