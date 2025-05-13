from db.database import SessionLocal
from models.bots.grid_bot import GridBot
from quant_core.services.core_logger import CoreLogger


def get_all_grid_bots() -> list[GridBot]:
    """Fetch all grid bots from the database."""
    with SessionLocal() as session:
        CoreLogger().info("Fetching all grid bots from the database.")
        return session.query(GridBot).all()


def get_grid_bot_by_uid(uid: str) -> GridBot | None:
    """Fetch a single grid bot by UID."""
    with SessionLocal() as session:
        CoreLogger().info(f"Fetching grid bot with uid: {uid}")
        return session.query(GridBot).filter_by(uid=uid).first()


def upsert_grid_bot(
    uid: str,
    account_uid: str,
    name: str,
    symbol: str,
    lower_bound: float,
    upper_bound: float,
    n_grids: int,
    base_order_size_percent: float,
):
    with SessionLocal() as session:
        CoreLogger().info(
            f"Upserting grid bot {uid} for account_uid={account_uid}, symbol={symbol}, "
            f"range=({lower_bound}-{upper_bound}), n_grids={n_grids}, size_pct={base_order_size_percent}"
        )
        bot = session.query(GridBot).filter_by(uid=uid).first()

        if bot:
            bot.name = name
            bot.account_uid = account_uid
            bot.symbol = symbol
            bot.lower_bound = lower_bound
            bot.upper_bound = upper_bound
            bot.n_grids = n_grids
            bot.base_order_size_percent = base_order_size_percent
        else:
            bot = GridBot(
                uid=uid,
                account_uid=account_uid,
                name=name,
                symbol=symbol,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                n_grids=n_grids,
                base_order_size_percent=base_order_size_percent,
            )
            session.add(bot)

        session.commit()
        return bot


def delete_grid_bot(uid: str):
    if not uid:
        CoreLogger().warning("Tried to delete grid bot without UID.")
        return

    with SessionLocal() as session:
        bot = session.query(GridBot).filter_by(uid=uid).first()
        if bot:
            session.delete(bot)
            session.commit()
            CoreLogger().info(f"Deleted grid bot {uid}.")
        else:
            CoreLogger().warning(f"No grid bot found for UID: {uid}")


def toggle_grid_bot_enabled(uid: str) -> GridBot | None:
    with SessionLocal() as session:
        bot = session.query(GridBot).filter_by(uid=uid).first()
        if bot:
            bot.enabled = not bot.enabled
            CoreLogger().info(f"Toggled grid bot {uid} to {'ENABLED' if bot.enabled else 'DISABLED'}.")
            session.commit()

        return bot
