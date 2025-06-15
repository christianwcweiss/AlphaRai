from typing import List

from db.database import CacheSessionLocal
from models.cache.signals import Signal
from quant_core.services.core_logger import CoreLogger


class SignalService:
    """Service class for managing trading signals in the cache database."""

    @staticmethod
    def store_signal(signal: Signal) -> Signal:
        """Store a new signal."""
        with CacheSessionLocal() as session:
            try:
                session.add(signal)
                session.commit()
                CoreLogger().info(f"Stored signal {signal}")
                return signal
            except Exception as error:
                session.rollback()
                CoreLogger().error(f"Failed to store signal: {error}")
                raise

    @staticmethod
    def get_all_signals() -> List[Signal]:
        """Fetch all signals from the database."""
        with CacheSessionLocal() as session:
            CoreLogger().debug("Fetching all signals from the cache.")
            return session.query(Signal).all()

    @staticmethod
    def delete_all_signals() -> None:
        """Delete all signal records from the database."""
        with CacheSessionLocal() as session:
            try:
                deleted = session.query(Signal).delete()
                session.commit()
                CoreLogger().info(f"Deleted all signals ({deleted} rows).")
            except Exception as error:
                session.rollback()
                CoreLogger().error(f"Failed to delete all signals: {error}")
                raise

    @staticmethod
    def delete_signal_by_id(signal_id: int) -> None:
        """Delete a single signal by its primary key ID."""
        with CacheSessionLocal() as session:
            signal = session.query(Signal).filter_by(id=signal_id).first()
            if signal:
                session.delete(signal)
                session.commit()
                CoreLogger().info(f"Deleted signal with ID {signal_id}")
            else:
                CoreLogger().warning(f"No signal found with ID {signal_id}")
