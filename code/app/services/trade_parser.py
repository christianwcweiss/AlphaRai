import re
from entities.trade_details import TradeDetails


class TradeMessageParser:
    @staticmethod
    def parse(message: str) -> TradeDetails:
        lines = message.strip().splitlines()

        # Extract symbol and direction (no change here)
        symbol = lines[0].strip()
        direction = lines[1].split('=')[1].strip()  # Extract direction from 'Direction = TradeDirection.SELL'

        # Extract timeframe (no change here)
        timeframe = lines[2].split('=')[1].strip()  # Extract time from 'Timeframe = 2025-05-01T20:10:19Z'

        # Extract entry, stop loss, and take profit values
        data = {}
        for line in lines[3:]:
            if "=" not in line:
                continue
            key, value = map(str.strip, line.split("=", 1))
            try:
                value = float(value)
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