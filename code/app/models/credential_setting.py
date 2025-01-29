from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CredentialSetting(Base):
    __tablename__ = "credential_settings"

    id = Column(Integer, primary_key=True)
    uid = Column(String(8), nullable=False, unique=True)
    platform = Column(String, nullable=False)
    friendly_name = Column(String, nullable=True)
    secret_name = Column(String, nullable=False)
    enabled = Column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return (
            f"<CredentialSetting(id={self.id}, uid={self.uid}, platform={self.platform}, "
            f"friendly_name={self.friendly_name}, secret_name={self.secret_name}, enabled={self.enabled})>"
        )