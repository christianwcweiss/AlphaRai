import re
from entities.trade_details import TradeDetails


class TradeMessageParser:
    @staticmethod
    def parse(message: str) -> TradeDetails:
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
                value = float(value.replace("%", ""))
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
            ai_confidence=data.get("AI Confidence")
        )
