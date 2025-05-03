# portfolio/portfolio_asset_repository.py
from sqlmodel import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from portfolio.models import PortfolioAsset


class PortfolioAssetRepository:

    @staticmethod
    async def add_asset(portfolio_id: int, asset_id: int, asset_type: str, quantity: float, price: float, db: AsyncSession):
        statement = select(PortfolioAsset).where(
            PortfolioAsset.portfolio_id == portfolio_id,
            PortfolioAsset.asset_id == asset_id,
            PortfolioAsset.asset_type == asset_type
        )
        result = await db.execute(statement)
        existing = result.scalars().first()

        if existing:
            return existing

        asset = PortfolioAsset(
            portfolio_id=portfolio_id,
            asset_id=asset_id,
            asset_type=asset_type,
            quantity=quantity,
            purchase_price=price
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)
        return asset

    @staticmethod
    async def update_asset(portfolio_id: int, asset_id: int, asset_type: str, quantity: float, price: float, db: AsyncSession):
        statement = select(PortfolioAsset).where(
            PortfolioAsset.portfolio_id == portfolio_id,
            PortfolioAsset.asset_id == asset_id,
            PortfolioAsset.asset_type == asset_type
        )
        result = await db.execute(statement)
        asset = result.scalars().first()

        if not asset:
            return False

        asset.quantity = quantity
        asset.purchase_price = price
        db.add(asset)
        await db.commit()
        return True

    @staticmethod
    async def remove_asset(portfolio_id: int, asset_id: int, asset_type: str, db: AsyncSession):
        statement = select(PortfolioAsset).where(
            PortfolioAsset.portfolio_id == portfolio_id,
            PortfolioAsset.asset_id == asset_id,
            PortfolioAsset.asset_type == asset_type
        )
        result = await db.execute(statement)
        asset = result.scalars().first()

        if not asset:
            return False

        await db.delete(asset)
        await db.commit()
        return True

    @staticmethod
    async def get_all_assets(portfolio_id: int, db: AsyncSession):
        statement = select(PortfolioAsset).where(PortfolioAsset.portfolio_id == portfolio_id)
        result = await db.execute(statement)
        return result.scalars().all()
