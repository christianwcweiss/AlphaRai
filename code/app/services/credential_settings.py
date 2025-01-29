from db.database import SessionLocal
from models.credential_setting import CredentialSetting
from quant_core.services.core_logger import CoreLogger


def get_all_credential_settings() -> list[CredentialSetting]:
    """Fetch all credential settings from the database."""
    with SessionLocal() as session:
        CoreLogger().info("Fetching all credential settings from the database.")
        return session.query(CredentialSetting).all()

def upsert_credential_settings(platform: str, friendly_name: str, secret_name: str, uid: str):
    with SessionLocal() as session:
        CoreLogger().info(f"Upserting credential settings for platform: {platform}, uid: {uid}, friendly_name: {friendly_name}, secret_name: {secret_name}")
        setting = session.query(CredentialSetting).filter_by(
            platform=platform,
            uid=uid
        ).first()

        if setting:
            setting.friendly_name = friendly_name
            setting.secret_name = secret_name
        else:
            setting = CredentialSetting(
                uid=uid,
                platform=platform,
                friendly_name=friendly_name,
                secret_name=secret_name
            )
            session.add(setting)

        session.commit()
        return setting


def delete_credential_settings(platform: str, uid: str) -> None:
    with SessionLocal() as session:
        session.query(CredentialSetting).filter_by(
            platform=platform,
            uid=uid
        ).delete()
        session.commit()

def toggle_credential_enabled(uid: str) -> CredentialSetting | None:
    with SessionLocal() as session:
        setting = session.query(CredentialSetting).filter_by(uid=uid).first()
        if setting:
            setting.enabled = not setting.enabled
            CoreLogger().info(f"Toggled account {uid} to {'ENABLED' if setting.enabled else 'DISABLED'}.")
            session.commit()
        return setting
