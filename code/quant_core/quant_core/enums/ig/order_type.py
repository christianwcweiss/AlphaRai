from enum import Enum


class IGOrderType(Enum):
    LIMIT = "LIMIT"
    LIMIT_ORDER = "LIMIT_ORDER"
    MARKET = "MARKET"
    QUOTE = "QUOTE"
