# portfolio/service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from portfolio.portfolio_repository import PortfolioRepository
from portfolio.portfolio_asset_repository import PortfolioAssetRepository
from portfolio.utils import set_cached_portfolio_assets, fetch_latest_price

from assets.models import Stock, ETF, Index, Cryptocurrency


class PortfolioService:
    asset_models = {
        "stock": Stock,
        "etf": ETF,
        "index": Index,
        "cryptocurrency": Cryptocurrency
    }

    @staticmethod
    async def get_or_create_portfolio(user_id: int, db: AsyncSession):
        return await PortfolioRepository.get_default_portfolio(user_id, db)

    @staticmethod
    async def add_asset(user_id: int, asset_id: int, asset_type: str, quantity: float, db: AsyncSession):
        portfolio = await PortfolioService.get_or_create_portfolio(user_id, db)
        model = PortfolioService.asset_models.get(asset_type.lower())

        if not model:
            raise ValueError("Invalid asset type")

        result = await db.execute(select(model).where(model.id == asset_id))
        asset = result.scalars().first()

        if not asset or not getattr(asset, "symbol", None):
            raise ValueError("Asset not found or missing symbol")

        latest_price = await fetch_latest_price(asset.symbol)
        if latest_price is None:
            raise ValueError("Failed to fetch price for asset")

        created = await PortfolioAssetRepository.add_asset(
            portfolio_id=portfolio.id,
            asset_id=asset_id,
            asset_type=asset_type,
            quantity=quantity,
            price=latest_price,
            db=db
        )

        await PortfolioService._refresh_cache(portfolio.id, db)
        return created

    @staticmethod
    async def update_asset(user_id: int, asset_id: int, asset_type: str, quantity: float, price: float, db: AsyncSession):
        portfolio = await PortfolioService.get_or_create_portfolio(user_id, db)
        updated = await PortfolioAssetRepository.update_asset(
            portfolio_id=portfolio.id,
            asset_id=asset_id,
            asset_type=asset_type,
            quantity=quantity,
            price=price,
            db=db
        )
        if updated:
            await PortfolioService._refresh_cache(portfolio.id, db)
        return updated

    @staticmethod
    async def remove_asset(user_id: int, asset_id: int, asset_type: str, db: AsyncSession):
        portfolio = await PortfolioService.get_or_create_portfolio(user_id, db)
        deleted = await PortfolioAssetRepository.remove_asset(
            portfolio_id=portfolio.id,
            asset_id=asset_id,
            asset_type=asset_type,
            db=db
        )
        if deleted:
            await PortfolioService._refresh_cache(portfolio.id, db)
        return deleted

    @staticmethod
    async def get_assets(user_id: int, db: AsyncSession):
        portfolio = await PortfolioService.get_or_create_portfolio(user_id, db)
        assets = await PortfolioAssetRepository.get_all_assets(portfolio.id, db)
        return await PortfolioService._enrich_assets(assets, db)

    @staticmethod
    async def _refresh_cache(portfolio_id: int, db: AsyncSession):
        assets = await PortfolioAssetRepository.get_all_assets(portfolio_id, db)
        enriched = await PortfolioService._enrich_assets(assets, db)
        await set_cached_portfolio_assets(portfolio_id, enriched)

    @staticmethod
    async def _enrich_assets(assets, db: AsyncSession):
        enriched = []

        for item in assets:
            model = PortfolioService.asset_models.get(item.asset_type.lower())
            if not model:
                continue

            result = await db.execute(select(model).where(model.id == item.asset_id))
            meta = result.scalars().first()

            if meta:
                name = getattr(meta, "name", None)
                if not name:
                    currency_base = getattr(meta, "currency_base", "")
                    currency_quote = getattr(meta, "currency_quote", "")
                    if currency_base and currency_quote:
                        name = f"{currency_base} / {currency_quote}"
                    else:
                        name = "Unknown"

                enriched.append({
                    "id": item.id,
                    "asset_id": item.asset_id,
                    "symbol": getattr(meta, "symbol", None),
                    "name": name,
                    "exchange": getattr(meta, "exchange", None),
                    "currency": getattr(meta, "currency", None),
                    "currency_base": getattr(meta, "currency_base", None),
                    "currency_quote": getattr(meta, "currency_quote", None),
                    "quantity": item.quantity,
                    "price": item.purchase_price,
                    "sum": item.quantity * item.purchase_price,
                    "type": item.asset_type,
                })

        return enriched
