from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class GridBot(Base):  # type: ignore  # pylint: disable=too-few-public-methods
    """Grid bot model for the application."""

    __tablename__ = "main_grid_bots"

    id = Column(Integer, primary_key=True)
    uid = Column(String(8), nullable=False, unique=True)  # Unique bot identifier
    account_uid = Column(String(8), nullable=False)  # Reference to Account.uid
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)

    lower_bound = Column(Float, nullable=False)
    upper_bound = Column(Float, nullable=False)
    n_grids = Column(Integer, nullable=False)
    base_order_size_percent = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint("account_uid", "symbol", name="uix_account_symbol"),)

    def __repr__(self) -> str:
        return (
            f"<GridBot(id={self.id}, uid={self.uid}, name={self.name}, account_uid={self.account_uid}, "
            f"symbol={self.symbol}, enabled={self.enabled}, range=({self.lower_bound}-{self.upper_bound}), "
            f"n_grids={self.n_grids}, order_size_pct={self.base_order_size_percent})>"
        )
