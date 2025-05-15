from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

from quant_core.entities.dto.trade import TradeDTO

Base = declarative_base()


class Trade(Base):  # type: ignore  # pylint: disable=too-few-public-methods
    """Trade model for SQLAlchemy ORM."""

    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, nullable=False)

    ticket = Column(Integer, nullable=False)
    order = Column(Integer, nullable=False)
    time = Column(DateTime, nullable=False)

    type = Column(Integer, nullable=False)
    entry = Column(Integer, nullable=False)
    size = Column(Float, nullable=False)

    symbol = Column(String(32), nullable=False)
    price = Column(Float, nullable=False)

    profit = Column(Float, nullable=False)

    swap = Column(Float, nullable=True)
    commission = Column(Float, nullable=True)
    magic = Column(Integer, nullable=True)
    comment = Column(String(255), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Trade(id={self.id}, ticket={self.ticket}, symbol={self.symbol}, "
            f"size={self.size}, profit={self.profit})>"
        )

    @staticmethod
    def from_dto(trade: TradeDTO) -> "Trade":
        """Create a Trade instance from a TradeDTO."""
        return Trade(
            id=trade.id,
            account_id=trade.account_id,
            ticket=trade.ticket,
            order=trade.order,
            time=trade.time,
            type=trade.type,
            entry=trade.entry,
            size=trade.size,
            symbol=trade.symbol,
            price=trade.price,
            profit=trade.profit,
            swap=trade.swap,
            commission=trade.commission,
            magic=trade.magic,
            comment=trade.comment,
        )

    def to_dto(self) -> TradeDTO:
        """Convert the Trade instance to a TradeDTO."""
        return TradeDTO(
            id=self.id,
            account_id=self.account_id,
            ticket=self.ticket,
            order=self.order,
            time=self.time,
            type=self.type,
            entry=self.entry,
            size=self.size,
            symbol=self.symbol,
            price=self.price,
            profit=self.profit,
            swap=self.swap,
            commission=self.commission,
            magic=self.magic,
            comment=self.comment,
        )
