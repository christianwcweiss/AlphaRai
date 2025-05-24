from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()


class BalanceOverTimeCache(Base):  # type: ignore
    """Cached result of balance over time."""

    __tablename__ = "cache_balance_over_time"

    id = Column(Integer, primary_key=True, autoincrement=True)

    account_id = Column(String, nullable=True)
    symbol = Column(String, nullable=True)
    direction = Column(String, nullable=True)
    asset_type = Column(String, nullable=True)
    hour = Column(Integer, nullable=True)
    weekday = Column(Integer, nullable=True)

    closed_at = Column(DateTime, nullable=False)

    initial_balance = Column(Float, nullable=False)
    absolute_balance = Column(Float, nullable=False)
    initial_balance_pct = Column(Float, nullable=False)
    relative_balance = Column(Float, nullable=False)

    cached_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)

    __table_args__ = (
        Index("ix_balance_cache_group", "account_id", "symbol", "asset_type", "hour", "weekday"),
        Index("ix_balance_cache_closed_at", "closed_at"),
    )

    def __repr__(self) -> str:
        parts = [
            f"{f}={getattr(self, f)}"
            for f in ["account_id", "symbol", "asset_type", "direction", "hour", "weekday"]
            if getattr(self, f) is not None
        ]
        return f"<BalanceOverTimeCache({', '.join(parts)}, closed_at={self.closed_at})>"
