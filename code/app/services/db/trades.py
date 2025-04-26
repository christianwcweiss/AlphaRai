from sqlalchemy import text

from db.database import SessionLocal
from models.trades import Trade
from quant_core.services.core_logger import CoreLogger


def get_all_trades() -> list[Trade]:
    """Fetch all trades from the database."""
    with SessionLocal() as session:
        CoreLogger().info("Fetching all trades from the database.")
        return session.query(Trade).all()


def get_trade_by_ticket(ticket: int) -> Trade | None:
    """Fetch a single trade by ticket."""
    with SessionLocal() as session:
        CoreLogger().info(f"Fetching trade with ticket: {ticket}")
        return session.query(Trade).filter_by(ticket=ticket).first()


def upsert_trade(trade_data: dict, account_id: int):
    """
    Insert or update a trade based on ticket number.

    trade_data should include fields matching the Trade model (except id/account_id).
    """
    with SessionLocal() as session:
        ticket = trade_data.get("ticket")
        CoreLogger().info(f"Upserting trade with ticket: {ticket} for account_id: {account_id}")

        trade = session.query(Trade).filter_by(ticket=ticket, account_id=account_id).first()

        if trade:
            for key, value in trade_data.items():
                if hasattr(trade, key):
                    setattr(trade, key, value)
        else:
            trade = Trade(account_id=account_id, **trade_data)
            session.add(trade)

        session.commit()
        return trade


def delete_trade(ticket: int, account_id: int) -> None:
    """Delete a trade by ticket and account_id."""
    with SessionLocal() as session:
        CoreLogger().info(f"Deleting trade with ticket: {ticket} for account_id: {account_id}")
        session.query(Trade).filter_by(ticket=ticket, account_id=account_id).delete()
        session.commit()


def delete_trades_for_account(account_id: int) -> None:
    """Delete all trades for a given account."""
    with SessionLocal() as session:
        CoreLogger().info(f"Deleting all trades for account_id: {account_id}")
        session.query(Trade).filter_by(account_id=account_id).delete()
        session.commit()


def truncate_trades_table() -> None:
    """Delete all trades in a SQLite-safe way."""
    with SessionLocal() as session:
        CoreLogger().info("Deleting all rows from trades table (SQLite compatible).")
        session.execute(text("DELETE FROM trades"))
        session.commit()