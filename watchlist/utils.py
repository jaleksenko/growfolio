# watchlist/utils.py
from watchlist.models import WatchlistAssetResponse
import redis
import json
import os
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from watchlist.models import Watchlist, WatchlistAsset
from watchlist.watchlist_repository import WatchlistRepository
from watchlist.watchlist_asset_repository import WatchlistAssetRepository

# 🔹 Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 🔹 Connect to Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
REDIS_TTL = int(os.getenv("REDIS_TTL", 86400))  # Cache expiration time (1 day)
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

async def get_cached_watchlist(user_id: int, db: AsyncSession):
    """✅ Retrieves the user's watchlist from Redis or the database"""
    logger.debug(f"🔍 Checking cache for watchlist:{user_id}")
    watchlist_data = redis_client.get(f"watchlist:{user_id}")

    if watchlist_data:
        watchlist_dict = json.loads(watchlist_data)
        logger.debug(f"✅ Watchlist found in cache: {watchlist_dict}")

        return Watchlist(**{k: v for k, v in watchlist_dict.items() if k != "assets"})

    logger.info(f"⚠️ No cached watchlist found for user {user_id}, fetching from the database.")
    db_watchlist = await WatchlistRepository.get_default_watchlist(user_id, db)

    if db_watchlist:
        await set_cached_watchlist(user_id, db_watchlist)
        return db_watchlist
    else:
        logger.error(f"❌ No watchlist found for user {user_id} in the database!")
        return None

async def get_cached_watchlist_assets(watchlist_id: int, db: AsyncSession):
    """Retrieve watchlist assets from Redis or the database."""
    cache_key = f"watchlist_assets:{watchlist_id}"
    logger.debug(f"🔍 Checking cache for {cache_key}")

    assets_data = redis_client.get(cache_key)
    if assets_data:
        try:
            assets_list = json.loads(assets_data)
            logger.debug(f"✅ Cache hit: {len(assets_list)} assets found for {cache_key}")
            return assets_list
        except json.JSONDecodeError:
            logger.error(f"❌ Failed to decode cache data for {cache_key}, falling back to DB.")
    
    # Cache miss: Fetch from database
    logger.info(f"⚠️ No cached assets found for watchlist {watchlist_id}, fetching from DB.")
    assets = await WatchlistAssetRepository.get_all_assets_in_watchlist(watchlist_id, db)
    
    if assets:
        logger.debug(f"✅ DB fetch success: {len(assets)} assets found. Storing in cache.")
        await set_cached_watchlist_assets(watchlist_id, assets)
        return assets
    else:
        logger.warning(f"⚠️ No assets found in DB for watchlist {watchlist_id}")

    return []

async def set_cached_watchlist(user_id: int, watchlist: Watchlist):
    """✅ Stores the watchlist in Redis without assets"""
    if not watchlist:
        logger.error(f"❌ Trying to cache None watchlist for user {user_id}")
        return

    watchlist_data = watchlist.model_dump(exclude={"assets"})
    for key in ["created_at", "updated_at"]:
        if key in watchlist_data and isinstance(watchlist_data[key], datetime):
            watchlist_data[key] = watchlist_data[key].isoformat()

    redis_client.setex(f"watchlist:{user_id}", timedelta(seconds=REDIS_TTL), json.dumps(watchlist_data))
    logger.debug(f"✅ Watchlist cached for user {user_id}")


async def set_cached_watchlist_assets(watchlist_id: int, assets: list[dict]):
    """✅ Stores watchlist assets in Redis with enriched data"""
    if not assets:
        logger.warning(f"⚠️ Trying to cache an empty assets list for watchlist {watchlist_id}")
        return

    try:
        cache_key = f"watchlist_assets:{watchlist_id}"
        
        # ✅ Convert `id` to string before storing
        for asset in assets:
            asset["id"] = str(asset["id"])

        # ✅ Log before setting Redis data
        logger.debug(f"Storing in Redis ({cache_key}): {json.dumps(assets, indent=2)}")

        redis_client.setex(cache_key, timedelta(seconds=86400), json.dumps(assets))  
        logger.debug(f"✅ Watchlist assets cached for {cache_key}")

    except Exception as e:
        logger.error(f"❌ Error storing watchlist assets in Redis: {e}", exc_info=True)
        raise  # ✅ Re-raise error to debug the source



async def clear_watchlist_cache(user_id: int, watchlist_id: int):
    """Clear watchlist and asset cache in Redis."""
    redis_client.delete(f"watchlist:{user_id}")
    redis_client.delete(f"watchlist_assets:{watchlist_id}")
    logger.info(f"🗑 Cleared cache for user {user_id} and watchlist {watchlist_id}")