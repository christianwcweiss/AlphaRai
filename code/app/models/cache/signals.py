from datetime import UTC, datetime
from typing import Optional

from entities.trade_details import TradeDetails
from quant_core.enums.trade_direction import TradeDirection
from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Signal(Base):  # type: ignore
    """Signal model for SQLAlchemy ORM."""

    __tablename__ = "cache_signals"

    id = Column(Integer, primary_key=True, autoincrement=True)

    symbol = Column(String(32), nullable=False)
    direction = Column(String(8), nullable=False)
    timeframe = Column(Integer, nullable=False)

    entry = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)

    take_profit_1 = Column(Float, nullable=True)
    take_profit_2 = Column(Float, nullable=True)
    take_profit_3 = Column(Float, nullable=True)

    created_at = Column(String, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<Signal(id={self.id}, symbol={self.symbol}, direction={self.direction}, "
            f"entry={self.entry}, sl={self.stop_loss}, tps={[self.take_profit_1, self.take_profit_2, self.take_profit_3]})>"
        )

    @staticmethod
    def from_parsed(trade: TradeDetails, date: Optional[str] = None) -> "Signal":
        """Create a Signal instance from a parsed trade object."""
        return Signal(
            symbol=trade.symbol,
            direction=trade.direction.value if isinstance(trade.direction, TradeDirection) else trade.direction,
            timeframe=trade.timeframe.value,
            entry=trade.entry,
            stop_loss=trade.stop_loss,
            take_profit_1=getattr(trade, "take_profit_1", None),
            take_profit_2=getattr(trade, "take_profit_2", None),
            take_profit_3=getattr(trade, "take_profit_3", None),
            created_at=date or datetime.now(UTC),
        )
