from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class StrategySetting(Base):
    __tablename__ = "strategy_settings"

    id = Column(Integer, primary_key=True)
    strategy_id = Column(String, nullable=False)  # 🔥 FK removed for testing
    strategy_hash = Column(String, nullable=False)
    account = Column(String, nullable=False)
    asset = Column(String, nullable=False)
    cron_expression = Column(String, nullable=True)
    enabled = Column(Boolean, default=False)

    def __repr__(self):
        return (
            f"<StrategySetting(strategy_id={self.strategy_id}, "
            f"account={self.account}, asset={self.asset}, enabled={self.enabled})>"
        )
