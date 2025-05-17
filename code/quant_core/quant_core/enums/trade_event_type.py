from enum import Enum


class TradeEventType(Enum):
    """
    Enum for trade event types.
    """

    DEPOSIT = 0
    WITHDRAW = 1
    SHORT = 2
    LONG = 3
