from typing import List, Optional

from db.database import MainSessionLocal
from models.main.general_setting import GeneralSetting


def get_all_settings() -> List[GeneralSetting]:
    """Get all settings."""
    with MainSessionLocal() as session:
        return session.query(GeneralSetting).all()


def get_setting_by_key(key: str) -> Optional[GeneralSetting]:
    """Get a setting by key."""
    with MainSessionLocal() as session:
        return session.query(GeneralSetting).filter_by(key=key).first()


def upsert_setting(key: str, value: str, is_secret: bool = False) -> GeneralSetting:
    """Insert or update a setting by key."""
    with MainSessionLocal() as session:
        setting = session.query(GeneralSetting).filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.is_secret = is_secret
        else:
            setting = GeneralSetting(key=key, value=value)
            session.add(setting)
        session.commit()
        session.refresh(setting)
        return setting


def delete_setting(key: str) -> None:
    """Delete a setting by key."""
    with MainSessionLocal() as session:
        session.query(GeneralSetting).filter_by(key=key).delete()
        session.commit()
