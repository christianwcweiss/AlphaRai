from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    UniqueConstraint,
)
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class GridBot(Base):
    __tablename__ = "grid_bots"

    id = Column(Integer, primary_key=True)
    uid = Column(String(8), nullable=False, unique=True)  # Unique bot identifier
    account_uid = Column(String(8), nullable=False)       # Reference to Account.uid
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)

    lower_bound = Column(Float, nullable=False)
    upper_bound = Column(Float, nullable=False)
    n_grids = Column(Integer, nullable=False)  # number of grids between bounds
    base_order_size_percent = Column(Float, nullable=False)  # e.g., 1.5 for 1.5%

    __table_args__ = (
        UniqueConstraint("account_uid", "symbol", name="uix_account_symbol"),
    )

    def __repr__(self) -> str:
        return (
            f"<GridBot(id={self.id}, uid={self.uid}, name={self.name}, account_uid={self.account_uid}, "
            f"symbol={self.symbol}, enabled={self.enabled}, range=({self.lower_bound}-{self.upper_bound}), "
            f"n_grids={self.n_grids}, order_size_pct={self.base_order_size_percent})>"
        )