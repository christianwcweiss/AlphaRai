from sqlalchemy import Column, String, Integer, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base

from quant_core.enums.time_period import TimePeriod

Base = declarative_base()


class ConfluenceConfig(Base):  # type: ignore  # pylint: disable=too-few-public-methods
    """Represents a confluence configuration in the database."""

    __tablename__ = "main_confluences"

    confluence_id = Column(String, primary_key=True)
    period = Column(Enum(TimePeriod), nullable=False)
    weight = Column(Integer, default=100)
    enabled = Column(Boolean, default=True)
