from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Trade(Base):
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

    commission = Column(Float, nullable=True)
    swap = Column(Float, nullable=True)
    profit = Column(Float, nullable=False)

    magic = Column(Integer, nullable=True)
    comment = Column(String(255), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Trade(id={self.id}, ticket={self.ticket}, symbol={self.symbol}, "
            f"size={self.size}, profit={self.profit})>"
        )