from models.main.main_base import Base
from quant_core.enums.trade_direction import EnabledTradeDirection
from sqlalchemy import Column, Enum, Float, ForeignKey, String
from sqlalchemy.orm import relationship


class ConfluenceConfig(Base):  # type: ignore  # pylint: disable=too-few-public-methods
    """Represents a confluence configuration for a specific account."""

    __tablename__ = "main_confluences"

    confluence_id = Column(String, primary_key=True)
    account_id = Column(String, ForeignKey("main_accounts.uid"), nullable=False)

    min_value = Column(Float, default=0.9, nullable=False)
    max_value = Column(Float, default=1.1, nullable=False)
    enabled_trade_direction = Column(Enum(EnabledTradeDirection), nullable=False)

    account = relationship("Account", back_populates="confluence_configs")
