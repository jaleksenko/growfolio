# watchlist/watchlist_repository.py
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from watchlist.models import Watchlist

class WatchlistRepository:
    """Handles database interactions for watchlists."""

    @staticmethod
    async def get_user_watchlists(user_id: int, db: AsyncSession) -> list[Watchlist]:
        """Fetch all watchlists for a given user."""
        statement = select(Watchlist).where(Watchlist.user_id == user_id)
        result = await db.execute(statement)
        return result.scalars().all()

    @staticmethod
    async def get_default_watchlist(user_id: int, db: AsyncSession) -> Watchlist:
        """Ensure the user has a default watchlist or create one if missing."""
        statement = select(Watchlist).where(Watchlist.user_id == user_id)
        result = await db.execute(statement)
        watchlist = result.scalars().first()

        if not watchlist:
            watchlist = Watchlist(name="main", user_id=user_id)
            db.add(watchlist)
            await db.commit()
            await db.refresh(watchlist)

        return watchlist
