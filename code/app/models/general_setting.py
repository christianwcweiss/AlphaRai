from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GeneralSetting(Base):
    __tablename__ = "general_settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=False)