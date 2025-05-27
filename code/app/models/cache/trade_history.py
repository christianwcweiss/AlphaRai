from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

from quant_core.entities.dto.trade import AlphaTradeDTO
from quant_core.enums.trade_direction import TradeDirection
from quant_core.enums.trade_event_type import TradeEventType

Base = declarative_base()


class Trade(Base):  # type: ignore  # pylint: disable=too-few-public-methods
    """Trade model for SQLAlchemy ORM."""

    __tablename__ = "cache_trades"

    id = Column(Integer, primary_key=True, autoincrement=True)

    position_id = Column(Integer, nullable=False)
    account_id = Column(String, nullable=False)

    order = Column(Integer, nullable=False)
    trade_group = Column(String(64), nullable=False)

    opened_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime, nullable=False)

    direction = Column(String, nullable=False)
    event = Column(Integer, nullable=False)

    size = Column(Float, nullable=False)
    symbol = Column(String(32), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)

    swap = Column(Float, nullable=True)
    commission = Column(Float, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Trade(id={self.id}, order={self.order}, symbol={self.symbol}, "
            f"size={self.size}, profit={self.profit})>"
        )

    @staticmethod
    def from_dto(account_id: str, trade: AlphaTradeDTO) -> "Trade":
        """Create a Trade instance from a TradeDTO."""
        return Trade(
            position_id=trade.id,
            account_id=account_id,
            order=trade.order,
            trade_group=trade.trade_group,
            opened_at=trade.opened_at,
            closed_at=trade.closed_at,
            direction=trade.direction.value,
            event=trade.event.value,
            size=trade.size,
            symbol=trade.symbol,
            entry_price=trade.entry_price,
            exit_price=trade.exit_price,
            profit=trade.profit,
            swap=trade.swap,
            commission=trade.commission,
        )

    def to_dto(self) -> AlphaTradeDTO:
        """Convert the Trade instance to a TradeDTO."""
        return AlphaTradeDTO(
            id=self.position_id,
            account_id=self.account_id,
            order=self.order,
            trade_group=self.trade_group,
            opened_at=self.opened_at,
            closed_at=self.closed_at,
            direction=TradeDirection(self.direction),
            event=TradeEventType(self.event),
            size=self.size,
            symbol=self.symbol,
            entry_price=self.entry_price,
            exit_price=self.exit_price,
            profit=self.profit,
            swap=self.swap,
            commission=self.commission,
        )
