from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GeneralSetting(Base):  # type: ignore  # pylint: disable=too-few-public-methods
    """General settings for the application."""

    __tablename__ = "main_general_settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=False)
