from sqlalchemy import Column, String, Float, Integer, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from quant_core.enums.asset_type import AssetType
from quant_core.enums.trade_mode import TradeMode

Base = declarative_base()


class AccountConfig(Base):  # type: ignore  # pylint: disable=too-few-public-methods
    """Account configuration for trading assets."""

    __tablename__ = "main_account_config"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, index=True)  # Renamed from uid
    signal_asset_id = Column(String, nullable=False)
    entry_stagger_method = Column(String, default="linear")
    n_staggers = Column(Integer, default=1)
    risk_percent = Column(Float, nullable=False, default=1)
    mode = Column(Enum(TradeMode), nullable=False, default=TradeMode.DEFAULT.value)
    enabled = Column(Boolean, default=False)

    # symbols
    platform_asset_id = Column(String, nullable=False)
    asset_type = Column(Enum(AssetType), nullable=True)
    lot_size = Column(Float, nullable=False, default=1.0)
    decimal_points = Column(Integer, nullable=False)

    def __repr__(self):
        return (
            f"<AccountConfig(account_id={self.account_id}, "
            f"symbol={self.signal_asset_id}, risk={self.risk_percent}%, "
            f"lot_size={self.lot_size}, staggers={self.n_staggers}, "
            f"method={self.entry_stagger_method}, decimals={self.decimal_points})>"
        )
