
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(String, primary_key=True)  # e.g. "example_tv"
    strategy_hash = Column(String, nullable=False)
    strategy_type = Column(String, nullable=False)
    friendly_name = Column(String, nullable=True)

    def __repr__(self):
        return f"<Strategy(id={self.id}, type={self.strategy_type})>"