from dataclasses import dataclass
from datetime import datetime

from quant_core.enums.trade_direction import TradeDirection
from quant_core.enums.trade_event_type import TradeEventType


@dataclass
class AlphaTradeDTO:  # pylint: disable=too-many-instance-attributes
    """DTO for Trade entity."""

    id: int
    account_id: str
    order: int
    trade_group: str
    opened_at: datetime
    closed_at: datetime
    direction: TradeDirection
    event: TradeEventType
    size: float
    symbol: str
    entry_price: float
    exit_price: float
    profit: float
    swap: float
    commission: float
