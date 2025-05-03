import logging
from datetime import datetime
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from assets.models import Stock, ETF, Index, Cryptocurrency
from watchlist.models import Watchlist, WatchlistAssetResponse
from watchlist.watchlist_repository import WatchlistRepository
from watchlist.watchlist_asset_repository import WatchlistAssetRepository
from watchlist.utils import (
    get_cached_watchlist, set_cached_watchlist, 
    clear_watchlist_cache, get_cached_watchlist_assets, 
    set_cached_watchlist_assets
)

# 🔹 Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class WatchlistService:
    """Handles watchlist operations, prioritizing Redis cache when available."""

    @staticmethod
    async def get_or_create_default_watchlist(user_id: int, db: AsyncSession) -> Watchlist:
        """
        Retrieve the user's watchlist, first checking Redis, then falling back to the database.
        """
        watchlist = await get_cached_watchlist(user_id, db)
        if watchlist:
            return watchlist

        # Cache miss → Fetch from database
        watchlist = await WatchlistRepository.get_default_watchlist(user_id, db)
        await set_cached_watchlist(user_id, watchlist)
        return watchlist

    @staticmethod
    async def get_watchlist_assets(user_id: int, db: AsyncSession):
        """✅ Retrieve assets for the user's watchlist, enrich data, and cache it."""
        watchlist = await WatchlistService.get_or_create_default_watchlist(user_id, db)

        # ✅ Fetch assets from database
        assets = await WatchlistAssetRepository.get_all_assets_in_watchlist(watchlist.id, db)

        # ✅ Fetch metadata for each asset
        enriched_assets = []
        for asset in assets:
            metadata = await WatchlistService.get_asset_metadata(asset.asset_id, asset.asset_type, db)
            enriched_assets.append({
                "id": asset.id,
                "asset_id": asset.asset_id,
                "asset_type": asset.asset_type,
                "symbol": metadata.get("symbol"),
                "name": metadata.get("name"),
                "exchange": metadata.get("exchange"),
                "currency": metadata.get("currency"),
                "group": metadata.get("group"),
                "currency_base": metadata.get("currency_base"),
                "currency_quote": metadata.get("currency_quote"),
                "added_at": asset.added_at.isoformat(),  # ✅ Ensure datetime is converted to string
            })

        # ✅ Store enriched data in Redis
        await set_cached_watchlist_assets(watchlist.id, enriched_assets)  

        return enriched_assets  # ✅ Return only enriched dictionaries

    @staticmethod
    async def get_asset_metadata(asset_id: int, asset_type: str, db: AsyncSession):
        """✅ Retrieve asset metadata (symbol, name, exchange) based on asset type"""
        asset_model_map = {
            "stock": Stock,
            "etf": ETF,
            "index": Index,
            "cryptocurrency": Cryptocurrency
        }

        asset_model = asset_model_map.get(asset_type.lower())
        if not asset_model:
            return {}

        query = select(asset_model).where(asset_model.id == asset_id)
        result = await db.execute(query)
        asset = result.scalars().first()

        if not asset:
            return {}

        return {
            "symbol": getattr(asset, "symbol", None),
            "name": getattr(asset, "name", None),
            "exchange": getattr(asset, "exchange", None),
            "currency": getattr(asset, "currency", None),
            "group": asset_type.lower(),  # Group is derived from asset type
            "currency_base": getattr(asset, "currency_base", None),
            "currency_quote": getattr(asset, "currency_quote", None),
        }


    @staticmethod
    async def add_asset_to_watchlist(user_id: int, asset_id: int, asset_type: str, db: AsyncSession):
        """✅ Add an asset to the user's watchlist and update Redis cache."""
        watchlist = await WatchlistService.get_or_create_default_watchlist(user_id, db)
        asset = await WatchlistAssetRepository.add_asset_to_watchlist(watchlist.id, asset_id, asset_type, db)

        # ✅ Fetch all assets again (ensuring the latest addition is included)
        assets = await WatchlistAssetRepository.get_all_assets_in_watchlist(watchlist.id, db)

        # ✅ Convert all `WatchlistAsset` objects into dictionaries before passing to Redis
        enriched_assets = []
        for asset in assets:
            metadata = await WatchlistService.get_asset_metadata(asset.asset_id, asset.asset_type, db)
            enriched_assets.append({
                "id": asset.id,
                "asset_id": asset.asset_id,
                "asset_type": asset.asset_type,
                "symbol": metadata.get("symbol"),
                "name": metadata.get("name"),
                "exchange": metadata.get("exchange"),
                "currency": metadata.get("currency"),
                "group": metadata.get("group"),
                "currency_base": metadata.get("currency_base"),
                "currency_quote": metadata.get("currency_quote"),
                "added_at": asset.added_at.isoformat() if isinstance(asset.added_at, datetime) else asset.added_at,
            })

        # ✅ Store enriched data in Redis
        await set_cached_watchlist_assets(watchlist.id, enriched_assets)

        # ✅ Return only the new asset with metadata
        return enriched_assets[-1]  # Return last added asset as dictionary


    @staticmethod
    async def remove_asset_from_watchlist(user_id: int, asset_id: int, asset_type: str, db: AsyncSession):
        """✅ Remove an asset from the user's watchlist and update Redis cache."""
        watchlist = await WatchlistService.get_or_create_default_watchlist(user_id, db)
        success = await WatchlistAssetRepository.remove_asset_from_watchlist(watchlist.id, asset_id, asset_type, db)

        if success:
            # ✅ Fetch remaining assets after deletion
            assets = await WatchlistAssetRepository.get_all_assets_in_watchlist(watchlist.id, db)

            # ✅ Convert objects to dictionaries before passing to Redis
            enriched_assets = []
            for asset in assets:
                metadata = await WatchlistService.get_asset_metadata(asset.asset_id, asset.asset_type, db)
                enriched_assets.append({
                    "id": asset.id,
                    "asset_id": asset.asset_id,
                    "asset_type": asset.asset_type,
                    "symbol": metadata.get("symbol"),
                    "name": metadata.get("name"),
                    "exchange": metadata.get("exchange"),
                    "currency": metadata.get("currency"),
                    "group": metadata.get("group"),
                    "currency_base": metadata.get("currency_base"),
                    "currency_quote": metadata.get("currency_quote"),
                    "added_at": asset.added_at.isoformat() if isinstance(asset.added_at, datetime) else asset.added_at,
                })

            # ✅ Update Redis with remaining assets
            await set_cached_watchlist_assets(watchlist.id, enriched_assets)

        return success