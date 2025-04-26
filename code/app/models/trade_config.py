from sqlalchemy import Column, String, Float, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TradeConfig(Base):
    __tablename__ = "trade_config"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, index=True)  # The account UID
    signal_asset_id = Column(String, nullable=False)
    platform_asset_id = Column(String, nullable=False)
    entry_stagger_method = Column(String, nullable=False)
    size_stagger_method = Column(String, nullable=False)
    n_staggers = Column(Integer, nullable=False)
    size = Column(Float, nullable=False)
    decimal_points = Column(Integer, nullable=False)

    def __repr__(self):
        return (
            f"<TradeConfig("
            f"id={self.id}, "
            f"uid={self.uid}, "
            f"signal_asset_id={self.signal_asset_id}, "
            f"platform_asset_id={self.platform_asset_id}, "
            f"entry_stagger_method={self.entry_stagger_method}, "
            f"size_stagger_method={self.size_stagger_method}, "
            f"n_staggers={self.n_staggers}, "
            f"size={self.size}, "
            f"decimal_points={self.decimal_points}"
            f")>"
        )
