# assets/utils.py
import logging
import httpx
import json
import redis.asyncio as redis
from typing import Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel
from sqlalchemy import select
from assets.models import Stock, ETF, Index, Cryptocurrency
import os


logger = logging.getLogger(__name__)

# Get API_URL from environment
API_URL = os.getenv("API_URL", "https://api.twelvedata.com")

# Define ASSET_TYPE_MODELS
ASSET_TYPE_MODELS = {
    "stocks": Stock,
    "etfs": ETF,
    "indices": Index,
    "cryptocurrencies": Cryptocurrency,
}

# Define all API TYPE URLs
ASSET_TYPE_URLS = {
    "stocks": f"{API_URL}/stocks",
    "etfs": f"{API_URL}/etfs",
    "indices": f"{API_URL}/indices",
    "cryptocurrencies": f"{API_URL}/cryptocurrencies",
}

# Define API_TO_MODEL_MAPPING
API_TO_MODEL_MAPPING = {
    "stocks": {
        "symbol": "symbol",
        "name": "name",
        "currency": "currency",
        "exchange": "exchange",
    },
    "etfs": {
        "symbol": "symbol",
        "name": "name",
        "currency": "currency",
        "exchange": "exchange",
    },
    "indices": {
        "symbol": "symbol",
        "name": "name",
        "currency": "currency",
        "exchange": "exchange",
    },
    "cryptocurrencies": {
        "symbol": "symbol",
        "currency_base": "currency_base",
        "currency_quote": "currency_quote",
        "available_exchanges": "available_exchanges",
    }
}


async def fetch_data_from_api(url: str, max_retries: int = 3) -> list[dict]:
    """
    Fetch data from an API with retries.
    """
    timeout = httpx.Timeout(15.0, connect=10.0, read=10.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(1, max_retries + 1):
            try:
                logging.info(f"Fetching data from API: {url} (Attempt {attempt}/{max_retries})")
                response = await client.get(url)
                response.raise_for_status()
                data = response.json().get("data", [])

                if not isinstance(data, list):
                    logging.error(f"Unexpected API response format: {response.json()}")
                    return []

                return data

            except Exception as e:
                logging.error(f"API Error: {e}")

            await asyncio.sleep(2 ** attempt)

    logging.error("API retries failed.")
    return []



async def transform_data(data: list[dict], asset_type: str) -> list[dict]:
    """
    Transforms API data before inserting into the database.
    Ensures all required fields exist and removes duplicate (symbol, exchange) pairs.
    """
    transformed_data = []
    seen = set()  # Use a set to track unique (symbol, exchange) pairs

    required_fields = {
        "stocks": ["symbol", "exchange", "name", "currency"],
        "etfs": ["symbol", "exchange", "name", "currency"],
        "indices": ["symbol", "exchange", "name", "currency"],
        "cryptocurrencies": ["symbol", "currency_base", "currency_quote", "available_exchanges"],
    }

    for item in data:
        if any(not item.get(field) for field in required_fields[asset_type]):
            logger.warning(f"⚠️ Skipping record due to missing or empty fields: {item}")
            continue
        
        if asset_type == "cryptocurrencies":
            # 🔹 Cryptocurrencies may have several exchanges
            symbol = item["symbol"]
            currency_base = item["currency_base"]
            currency_quote = item["currency_quote"]
            exchanges = item.get("available_exchanges", [])

            # If there're no exchanges - skip
            if not exchanges:
                logger.warning(f"⚠️ Cryptocurrency without exchange has skipped: {item}")
                continue

            # Create separate record for each exchange
            for exchange in exchanges:
                key = (symbol, exchange)
                if key in seen:
                    continue  # Unique record (symbol, exchange)

                seen.add(key)
                transformed_data.append({
                    "symbol": symbol,
                    "exchange": exchange,
                    "currency_base": currency_base,
                    "currency_quote": currency_quote,
                })

        else:
            # 🔹 For stocks, etfs & indices
            symbol = item["symbol"]
            exchange = item["exchange"]
            name = item["name"]
            currency = item["currency"]

            key = (symbol, exchange)
            if key in seen:
                continue  # Skip duplicates

            seen.add(key)
            transformed_data.append({field: item[field] for field in required_fields[asset_type]})

    return transformed_data





async def update_redis_assets(session: AsyncSession, redis_url: str, asset_model: SQLModel, asset_type: str):
    """
    Updates Redis cache with the latest data from the database.
    - Data is stored in JSON format.
    - Uses a single key `{asset_type}:all_assets` for frontend access.
    """

    logger.info(f"Updating Redis cache for {asset_type}...")

    redis_client = redis.from_url(redis_url, decode_responses=True)
    
    # Remove old cache
    main_key = f"{asset_type}:all_assets"
    await redis_client.delete(main_key)

    # Fetch all assets from the database
    rows = (await session.execute(select(asset_model))).scalars().all()

    # Prepare JSON data for Redis
    if asset_type == "cryptocurrencies":
        json_data = json.dumps([
            {"id": str(row.id), "symbol": row.symbol, "exchange": row.exchange,
             "currency_base": row.currency_base, "currency_quote": row.currency_quote}
            for row in rows
        ])
    else:
        json_data = json.dumps([
            {"id": str(row.id), "symbol": row.symbol, "exchange": row.exchange, "name": row.name, "currency": row.currency}
            for row in rows
        ])

    # Save to Redis
    await redis_client.set(main_key, json_data)
    logger.info(f"Redis cache updated for {asset_type}.")