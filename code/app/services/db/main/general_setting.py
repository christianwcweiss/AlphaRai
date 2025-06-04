from typing import List, Optional

from db.database import MainSessionLocal
from models.main.general_setting import GeneralSetting


class GeneralSettingService:
    """Service class for managing general settings in the database."""

    @staticmethod
    def get_all_settings() -> List[GeneralSetting]:
        """Get all settings."""
        with MainSessionLocal() as session:
            return session.query(GeneralSetting).all()

    @staticmethod
    def get_setting_by_key(key: str) -> Optional[GeneralSetting]:
        """Get a setting by key."""
        with MainSessionLocal() as session:
            return session.query(GeneralSetting).filter_by(key=key).first()

    @staticmethod
    def upsert_setting(key: str, value: str) -> GeneralSetting:
        """Insert or update a setting by key."""
        with MainSessionLocal() as session:
            setting = session.query(GeneralSetting).filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                setting = GeneralSetting(key=key, value=value)
                session.add(setting)
            session.commit()
            session.refresh(setting)

            return setting

    @staticmethod
    def delete_setting(key: str) -> None:
        """Delete a setting by key."""
        with MainSessionLocal() as session:
            session.query(GeneralSetting).filter_by(key=key).delete()
            session.commit()


def get_all_settings() -> List[GeneralSetting]:
    """Get all settings."""
    with MainSessionLocal() as session:
        return session.query(GeneralSetting).all()


def get_setting_by_key(key: str) -> Optional[GeneralSetting]:
    """Get a setting by key."""
    with MainSessionLocal() as session:
        return session.query(GeneralSetting).filter_by(key=key).first()


def upsert_setting(key: str, value: str) -> GeneralSetting:
    """Insert or update a setting by key."""
    with MainSessionLocal() as session:
        setting = session.query(GeneralSetting).filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = GeneralSetting(key=key, value=value)
            session.add(setting)
        session.commit()
        session.refresh(setting)

        return setting


def delete_setting(key: str) -> None:
    """Delete a setting by key."""
    with MainSessionLocal() as session:
        """Delete a general setting by its key."""
        session.query(GeneralSetting).filter_by(key=key).delete()
        session.commit()
