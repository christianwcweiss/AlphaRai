from models.main.main_base import Base
from quant_core.enums.asset_type import AssetType
from quant_core.enums.stagger_method import StaggerMethod
from quant_core.enums.trade_mode import TradeMode
from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, Integer, PrimaryKeyConstraint, String
from sqlalchemy.orm import relationship


class AccountConfig(Base):  # type: ignore  # pylint: disable=too-few-public-methods
    """Account configuration for trading assets."""

    __tablename__ = "main_account_config"
    __table_args__ = (PrimaryKeyConstraint("account_id", "platform_asset_id", name="pk_account_asset"),)

    account_id = Column(String, ForeignKey("main_accounts.uid"), nullable=False)
    platform_asset_id = Column(String, nullable=False)

    signal_asset_id = Column(String, nullable=False)
    entry_stagger_method = Column(Enum(StaggerMethod), default=StaggerMethod.FIBONACCI.name)
    entry_offset = Column(Float, nullable=False, default=0.0)
    n_staggers = Column(Integer, default=1)
    risk_percent = Column(Float, nullable=False, default=1)
    mode = Column(Enum(TradeMode), nullable=False, default=TradeMode.DEFAULT.name)

    asset_type = Column(Enum(AssetType), nullable=True)
    lot_size = Column(Float, nullable=False, default=1.0)
    decimal_points = Column(Integer, nullable=False)

    enabled = Column(Boolean, default=False)

    account = relationship("Account", back_populates="account_configs")

    def __repr__(self):
        return (
            f"<AccountConfig("
            f"account_id={self.account_id}, "
            f"platform_asset_id={self.platform_asset_id}, "
            f"signal_asset_id={self.signal_asset_id}, "
            f"entry_stagger_method={self.entry_stagger_method}, "
            f"entry_offset={self.entry_offset}, "
            f"n_staggers={self.n_staggers}, "
            f"risk_percent={self.risk_percent}, "
            f"mode={self.mode}, "
            f"asset_type={self.asset_type}, "
            f"lot_size={self.lot_size}, "
            f"decimal_points={self.decimal_points}, "
            f"enabled={self.enabled}"
            f")>"
        )
