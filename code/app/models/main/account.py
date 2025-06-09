from sqlalchemy import Boolean, Column, Enum, String
from sqlalchemy.orm import relationship
from models.main.main_base import Base

from quant_core.entities.dto.account import AccountDTO
from quant_core.enums.platform import Platform
from quant_core.enums.prop_firm import PropFirm


class Account(Base):  # type: ignore  # pylint: disable=too-few-public-methods
    """Represents an account in the database."""

    __tablename__ = "main_accounts"

    uid = Column(String(8), primary_key=True)
    platform = Column(Enum(Platform), nullable=False)
    prop_firm = Column(Enum(PropFirm), nullable=False)
    friendly_name = Column(String, nullable=False)

    # Either secret name or credentials
    secret_name = Column(String, nullable=True)
    mt5_username = Column(String, nullable=True)
    mt5_password = Column(String, nullable=True)
    mt5_server = Column(String, nullable=True)

    enabled = Column(Boolean, nullable=False, default=False)

    account_configs = relationship(
        "AccountConfig",
        back_populates="account",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Account("
            f"uid={self.uid}, "
            f"platform={self.platform}, "
            f"prop_firm={self.prop_firm}, "
            f"friendly_name={self.friendly_name}, "
            f"secret_name={self.secret_name}, "
            f"mt5_username={self.mt5_username}, "
            f"mt5_password={'***' if self.mt5_password else None}, "
            f"mt5_server={self.mt5_server}, "
            f"enabled={self.enabled}"
            f")>"
        )

    @staticmethod
    def from_dto(dto: AccountDTO) -> "Account":
        """Create an Account instance from a DTO."""
        return Account(
            uid=dto.uid,
            platform=dto.platform,
            prop_firm=dto.prop_firm,
            friendly_name=dto.friendly_name,
            secret_name=dto.secret_name,
            mt5_username=dto.mt5_username,
            mt5_password=dto.mt5_password,
            mt5_server=dto.mt5_server,
            enabled=dto.enabled,
        )

    def to_dto(self) -> AccountDTO:
        """Convert the account to a DTO."""
        return AccountDTO(
            uid=self.uid,
            platform=self.platform,
            prop_firm=self.prop_firm,
            friendly_name=self.friendly_name,
            secret_name=self.secret_name,
            mt5_username=self.mt5_username,
            mt5_password=self.mt5_password,
            mt5_server=self.mt5_server,
            enabled=self.enabled,
        )
