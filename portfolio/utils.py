# portfolio/utils.py
import httpx
import redis
import json
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from portfolio.models import Portfolio, PortfolioAsset
from portfolio.portfolio_repository import PortfolioRepository
from portfolio.portfolio_asset_repository import PortfolioAssetRepository


logger = logging.getLogger(__name__)


# --- Environment Settings ---
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL")
REDIS_URL = os.getenv("REDIS_URL")
REDIS_TTL = int(os.getenv("REDIS_TTL"))
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

async def get_cached_portfolio(user_id: int, db: AsyncSession):
    key = f"portfolio:{user_id}"
    cached = redis_client.get(key)

    if cached:
        return Portfolio(**json.loads(cached))

    portfolio = await PortfolioRepository.get_default_portfolio(user_id, db)
    if portfolio:
        await set_cached_portfolio(user_id, portfolio)
    return portfolio

async def get_cached_portfolio_assets(portfolio_id: int, db: AsyncSession):
    key = f"portfolio_assets:{portfolio_id}"
    cached = redis_client.get(key)

    if cached:
        return json.loads(cached)

    assets = await PortfolioAssetRepository.get_all_assets(portfolio_id, db)
    enriched = []
    for a in assets:
        enriched.append({
            "id": str(a.id),
            "asset_id": a.asset_id,
            "asset_type": a.asset_type,
            "quantity": a.quantity,
            "purchase_price": a.purchase_price,
            "sum": round(a.quantity * a.purchase_price, 2),
            "added_at": a.added_at.isoformat(),
        })

    await set_cached_portfolio_assets(portfolio_id, enriched)
    return enriched

async def set_cached_portfolio(user_id: int, portfolio: Portfolio):
    key = f"portfolio:{user_id}"
    data = portfolio.model_dump(exclude={"assets"})
    for k in ["created_at", "updated_at"]:
        if k in data and isinstance(data[k], datetime):
            data[k] = data[k].isoformat()
    redis_client.setex(key, timedelta(seconds=REDIS_TTL), json.dumps(data))

async def set_cached_portfolio_assets(portfolio_id: int, assets: list[dict]):
    key = f"portfolio_assets:{portfolio_id}"
    redis_client.setex(key, timedelta(seconds=REDIS_TTL), json.dumps(assets))

async def clear_portfolio_cache(user_id: int, portfolio_id: int):
    redis_client.delete(f"portfolio:{user_id}")
    redis_client.delete(f"portfolio_assets:{portfolio_id}")

async def fetch_latest_price(symbol: str) -> float | None:
    if not API_URL or not API_KEY:
        print("❌ Missing API_URL or API_KEY")
        return None

    url = f"{API_URL}/price?symbol={symbol}&apikey={API_KEY}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            print(f"📡 Fetching price for {symbol}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Price data: {data}")
                price = data.get("price")
                if price:
                    return float(price)
                else:
                    print(f"⚠️ No 'price' in response for {symbol}: {data}")
            else:
                print(f"❌ Failed request: {response.text}")
    except Exception as e:
        print(f"❌ Exception while fetching price for {symbol}: {e}")
    return None

