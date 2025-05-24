from enum import Enum


class OrderType(Enum):
    """Order types for trading platforms."""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
