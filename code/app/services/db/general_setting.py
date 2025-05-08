from db.database import SessionLocal
from models.general_setting import GeneralSetting


def get_all_settings() -> list[GeneralSetting]:
    with SessionLocal() as session:
        return session.query(GeneralSetting).all()


def get_setting_by_key(key: str) -> GeneralSetting | None:
    with SessionLocal() as session:
        return session.query(GeneralSetting).filter_by(key=key).first()


def upsert_setting(key: str, value: str, is_secret: bool = False) -> GeneralSetting:
    with SessionLocal() as session:
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


def delete_setting(key: str):
    with SessionLocal() as session:
        session.query(GeneralSetting).filter_by(key=key).delete()
        session.commit()
