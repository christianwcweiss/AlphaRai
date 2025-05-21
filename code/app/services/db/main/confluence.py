from db.database import MainSessionLocal
from models.main.confluence import ConfluenceConfig
from quant_core.services.core_logger import CoreLogger
from quant_core.enums.time_period import TimePeriod


def get_all_confluences() -> list[ConfluenceConfig]:
    """Fetch all confluence configs from the database."""
    with MainSessionLocal() as session:
        CoreLogger().info("Fetching all confluence configs from the database.")
        return session.query(ConfluenceConfig).all()


def get_confluence_by_id(confluence_id: str) -> ConfluenceConfig | None:
    """Fetch a single confluence config by ID."""
    with MainSessionLocal() as session:
        CoreLogger().info(f"Fetching confluence with ID: {confluence_id}")
        return session.query(ConfluenceConfig).filter_by(confluence_id=confluence_id).first()


def upsert_confluence(confluence_id: str, period: TimePeriod, weight: int = 100, enabled: bool = True):
    """Insert or update a confluence config."""
    with MainSessionLocal() as session:
        CoreLogger().info(f"Upserting confluence: {confluence_id} ({period.name}) with weight={weight}")
        con = session.query(ConfluenceConfig).filter_by(confluence_id=confluence_id).first()

        if con:
            con.period = period
            con.weight = weight
            con.enabled = enabled
        else:
            con = ConfluenceConfig(confluence_id=confluence_id, period=period, weight=weight, enabled=enabled)
            session.add(con)

        session.commit()
        return con


def delete_confluence(confluence_id: str):
    """Delete a confluence config by ID."""
    with MainSessionLocal() as session:
        CoreLogger().info(f"Deleting confluence: {confluence_id}")
        session.query(ConfluenceConfig).filter_by(confluence_id=confluence_id).delete()
        session.commit()


def toggle_confluence_enabled(confluence_id: str) -> ConfluenceConfig | None:
    """Toggle enabled status of a confluence."""
    with MainSessionLocal() as session:
        con = session.query(ConfluenceConfig).filter_by(confluence_id=confluence_id).first()
        if con:
            con.enabled = not con.enabled
            CoreLogger().info(f"Toggled confluence {confluence_id} to {'ENABLED' if con.enabled else 'DISABLED'}.")
            session.commit()
        return con
