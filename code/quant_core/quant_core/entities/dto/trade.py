from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TradeDTO:
    """DTO for Trade entity."""

    id: int
    account_id: int
    ticket: int
    order: int
    time: datetime
    type: int
    entry: int
    size: float
    symbol: str
    price: float
    profit: float
    swap: Optional[float] = None
    commission: Optional[float] = None
    magic: Optional[int] = None
    comment: Optional[str] = None
