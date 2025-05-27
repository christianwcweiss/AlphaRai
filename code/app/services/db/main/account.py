from typing import Optional, List

from db.database import MainSessionLocal
from models.main.account import Account
from quant_core.services.core_logger import CoreLogger


def get_all_accounts() -> List[Account]:
    """Fetch all credential settings from the database."""
    with MainSessionLocal() as session:
        CoreLogger().debug("Fetching all accounts from the database.")
        return session.query(Account).all()


def get_account_by_uid(uid: str) -> Optional[Account]:
    """Fetch a single account by UID."""
    with MainSessionLocal() as session:
        CoreLogger().debug(f"Fetching account with uid: {uid}")
        return session.query(Account).filter_by(uid=uid).first()


def upsert_account(platform: str, friendly_name: str, secret_name: str, uid: str) -> Account:
    """Upsert an account in the database."""
    with MainSessionLocal() as session:
        CoreLogger().info(
            f"Upserting credential settings for platform: "
            f"{platform}, uid: {uid}, friendly_name: {friendly_name}, secret_name: {secret_name}"
        )
        account = session.query(Account).filter_by(platform=platform, uid=uid).first()

        if account:
            account.friendly_name = friendly_name
            account.secret_name = secret_name
        else:
            account = Account(uid=uid, platform=platform, friendly_name=friendly_name, secret_name=secret_name)
            session.add(account)

        session.commit()

        return account


def delete_account(platform: str, uid: str) -> None:
    """Delete an account by platform and UID."""
    with MainSessionLocal() as session:
        account = session.query(Account).filter_by(platform=platform, uid=uid).first()
        if account:
            session.delete(account)
            session.commit()
            CoreLogger().info(f"Deleted account {uid}")
        else:
            CoreLogger().warning(f"No account found for UID: {uid}")


def toggle_account_enabled(uid: str) -> Account:
    """Toggle the enabled status of an account."""
    with MainSessionLocal() as session:
        account = session.query(Account).filter_by(uid=uid).first()
        if account:
            account.enabled = not account.enabled
            CoreLogger().info(f"Toggled account {uid} to {'ENABLED' if account.enabled else 'DISABLED'}.")
            session.commit()

        return account
