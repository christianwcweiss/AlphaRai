from sqlalchemy import Boolean, Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base

from quant_core.entities.dto.account import AccountDTO
from quant_core.enums.platform import Platform

Base = declarative_base()


class Account(Base):  # type: ignore  # pylint: disable=too-few-public-methods
    """Represents an account in the database."""

    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    uid = Column(String(8), nullable=False, unique=True)
    platform = Column(Enum(Platform), nullable=False)
    friendly_name = Column(String, nullable=True)
    secret_name = Column(String, nullable=False)
    enabled = Column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return (
            f"<Account(id={self.id}, uid={self.uid}, platform={self.platform}, "
            f"friendly_name={self.friendly_name}, secret_name={self.secret_name}, enabled={self.enabled})>"
        )

    @staticmethod
    def from_dto(dto: AccountDTO) -> "Account":
        """Create an Account instance from a DTO."""
        return Account(
            id=dto.id,
            uid=dto.uid,
            platform=dto.platform.value,
            friendly_name=dto.friendly_name,
            secret_name=dto.secret_name,
            enabled=dto.enabled,
        )

    def to_dto(self) -> AccountDTO:
        """Convert the account to a DTO."""
        return AccountDTO(
            id=self.id,
            uid=self.uid,
            platform=Platform(self.platform),
            friendly_name=self.friendly_name,
            secret_name=self.secret_name,
            enabled=self.enabled,
        )
