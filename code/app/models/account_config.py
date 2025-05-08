from sqlalchemy import Column, String, Float, Integer, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from quant_core.enums.asset_type import AssetType

Base = declarative_base()


class AccountConfig(Base):
    __tablename__ = "account_config"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, index=True)  # Renamed from uid
    signal_asset_id = Column(String, nullable=False)
    platform_asset_id = Column(String, nullable=False)

    # Trading logic
    entry_stagger_method = Column(String, default="linear")  # e.g., linear / fibonacci
    n_staggers = Column(Integer, default=1)

    # Risk configuration
    risk_percent = Column(Float, nullable=False, default=0.5)
    decimal_points = Column(Integer, nullable=False)  # from MT5
    lot_size = Column(Float, nullable=False, default=1.0)  # Needed for position size calc

    # Metadata
    asset_type = Column(Enum(AssetType), nullable=True)
    enabled = Column(Boolean, default=False)

    def __repr__(self):
        return (
            f"<AccountConfig(account_id={self.account_id}, "
            f"symbol={self.signal_asset_id}, risk={self.risk_percent}%, "
            f"lot_size={self.lot_size}, staggers={self.n_staggers}, "
            f"method={self.entry_stagger_method}, decimals={self.decimal_points})>"
        )
