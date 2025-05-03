# watchlist/watchlist_asset_repository.py
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from watchlist.models import WatchlistAsset

class WatchlistAssetRepository:
    """Handles database interactions for watchlist assets."""

    @staticmethod
    async def add_asset_to_watchlist(watchlist_id: int, asset_id: int, asset_type: str, db: AsyncSession):
        """Ensure the asset is not duplicated in the watchlist before adding."""
        # Check if the asset already exists in the watchlist
        statement = select(WatchlistAsset).where(
            WatchlistAsset.watchlist_id == watchlist_id,
            WatchlistAsset.asset_id == asset_id,
            WatchlistAsset.asset_type == asset_type
        )
        result = await db.execute(statement)
        existing_asset = result.scalars().first()

        if existing_asset:
            return existing_asset  # ✅ Return existing asset instead of adding a duplicate

        # If it does not exist, add the new asset
        asset = WatchlistAsset(watchlist_id=watchlist_id, asset_id=asset_id, asset_type=asset_type)
        db.add(asset)
        await db.commit()
        await db.refresh(asset)

        return asset


    @staticmethod
    async def remove_asset_from_watchlist(watchlist_id: int, asset_id: int, asset_type: str, db: AsyncSession) -> bool:
        """Remove an asset from a watchlist while ensuring type safety."""
        statement = select(WatchlistAsset).where(
            WatchlistAsset.watchlist_id == watchlist_id, 
            WatchlistAsset.asset_id == asset_id,
            WatchlistAsset.asset_type == asset_type  # ✅ Ensure the correct asset type is removed
        )
        result = await db.execute(statement)
        asset = result.scalars().first()

        if asset:
            await db.delete(asset)
            await db.commit()
            return True
        return False

    @staticmethod
    async def get_all_assets_in_watchlist(watchlist_id: int, db: AsyncSession) -> list[WatchlistAsset]:
        """Fetch all assets inside a specific watchlist from the database."""
        statement = select(WatchlistAsset).where(WatchlistAsset.watchlist_id == watchlist_id)
        result = await db.execute(statement)
        return result.scalars().all()
