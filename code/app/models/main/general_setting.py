from models.main.main_base import Base
from sqlalchemy import Column, String


class GeneralSetting(Base):  # type: ignore  # pylint: disable=too-few-public-methods
    """General settings for the application."""

    __tablename__ = "main_general_settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=False)
