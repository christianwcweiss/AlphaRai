from sqlalchemy import Column, String, Integer, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base

from quant_core.enums.time_period import TimePeriod

Base = declarative_base()

class ConfluenceConfig(Base):
    __tablename__ = "confluences"

    confluence_id = Column(String, primary_key=True)
    period = Column(Enum(TimePeriod), nullable=False)
    weight = Column(Integer, default=100)
    enabled = Column(Boolean, default=True)