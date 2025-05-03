# assets/services.py
import os
import redis.asyncio as redis
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, insert, select
from assets.repositories import AssetRepository
from assets.utils import fetch_data_from_api, transform_data, update_redis_assets, ASSET_TYPE_MODELS, ASSET_TYPE_URLS
import logging
import json


logger = logging.getLogger(__name__)


class AssetService:
    """
    The service handles:
      1) Determining which model + API URL to use based on asset_type.
      2) Fetching data from the external API.
      3) Transforming the data to match your SQLModel fields.
      4) Calling the repository to sync local DB + Redis.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the service with an async DB session and a Redis-based repository.
        """
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")  # Use env variable or default
        self.redis = redis.from_url(self.redis_url, decode_responses=True)

        self.repository = AssetRepository(session)
        self.session = session

    async def sync_assets(self, asset_type: str) -> dict:
        """
        1) Identify the correct SQLModel (Stock, ETF, etc.) from asset_type
        2) Build or retrieve the external API URL
        3) Fetch data from the API (async)
        4) Transform data to match local DB fields
        5) Insert new, remove old, update Redis
        """
        logger.info(f"Starting full sync for asset_type={asset_type}")

        # 1) Identify which SQLModel class to use
        model = ASSET_TYPE_MODELS.get(asset_type)
        if not model:
            raise HTTPException(status_code=400, detail=f"Invalid asset type: {asset_type}")

        # 2) Get the external API URL
        api_url = ASSET_TYPE_URLS.get(asset_type)
        if not api_url:
            raise HTTPException(status_code=400, detail=f"No API URL configured for {asset_type}")

        # 3) Fetch raw data from external API
        raw_data = await fetch_data_from_api(api_url)  # assumed async function from assets.utils
        if not raw_data:
            logger.warning(f"No data received from API for {asset_type}")
            return {"message": f"No data received for {asset_type}"}

        # 4) Transform data to match the SQLModel fields
        transformed_data = await transform_data(raw_data, asset_type)
        if not transformed_data:
            logger.warning(f"No transformed data for {asset_type}")
            return {"message": f"No transformed data for {asset_type}"}

        # 5) Call repository to sync local DB
        sync_result = await self.repository.sync_assets_with_api(model, transformed_data, asset_type)
        logger.info(f"Sync complete for {asset_type}: {sync_result}")

        # 6) Update Redis cache so it's consistent with the DB
        redis_url = os.getenv("REDIS_URL")
        await update_redis_assets(self.session, redis_url, model, asset_type)
        logger.info(f"Redis cache updated for {asset_type}")

        return {"result": sync_result}
    

    async def get_asset_symbols_from_redis(self, asset_type: str) -> list[dict]:
        """
        Retrieves asset symbols from Redis and converts `id` back to an integer.
        """
        cache_key = f"{asset_type}:all_assets"

        cached_data = await self.redis.get(cache_key)
        if cached_data:
            assets = json.loads(cached_data)                
            return assets
        return None


    async def get_asset_symbols_from_db(self, asset_type: str) -> list[dict]:
        """
        Retrieve asset symbols from the database.
        """
        model = ASSET_TYPE_MODELS.get(asset_type)
        if not model:
            raise HTTPException(status_code=400, detail="Invalid asset type")

        # 🔹 Determine the fields to select based on asset type
        if asset_type == "cryptocurrencies":
            query = select(model.id, model.symbol, model.exchange, model.currency_base, model.currency_quote)
        else:
            query = select(model.id, model.symbol, model.name, model.exchange, model.currency)

        result = await self.session.execute(query)
        assets = result.fetchall()

        if not assets:
            raise HTTPException(status_code=404, detail="No assets found")

        # 🔹 Format the asset list based on asset type
        if asset_type == "cryptocurrencies":
            assets_list = [
                {
                    "id": asset_id,
                    "symbol": symbol,
                    "exchange": exchange,
                    "currency_base": currency_base,
                    "currency_quote": currency_quote,
                }
                for asset_id, symbol, exchange, currency_base, currency_quote in assets
            ]
        else:
            assets_list = [
                {
                    "id": asset_id,
                    "symbol": symbol,
                    "name": name,
                    "exchange": exchange,
                    "currency": currency,
                }
                for asset_id, symbol, name, exchange, currency in assets
            ]

        # 🔹 Store the data in Redis with a 24-hour expiration
        cache_key = f"{asset_type}:all_assets"
        try:
            await self.redis.set(cache_key, json.dumps(assets_list), ex=86400)  # Set expiry to 24h
        except Exception as e:
            logger.error(f"Error saving to Redis: {e}")

        return assets_list
