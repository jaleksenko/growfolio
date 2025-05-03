# portfolio/portfolio_repository.py
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from portfolio.models import Portfolio

class PortfolioRepository:

    @staticmethod
    async def get_user_portfolios(user_id: int, db: AsyncSession) -> list[Portfolio]:
        statement = select(Portfolio).where(Portfolio.user_id == user_id)
        result = await db.execute(statement)
        return result.scalars().all()

    @staticmethod
    async def get_default_portfolio(user_id: int, db: AsyncSession) -> Portfolio:
        statement = select(Portfolio).where(Portfolio.user_id == user_id)
        result = await db.execute(statement)
        portfolio = result.scalars().first()

        if not portfolio:
            portfolio = Portfolio(name="main", user_id=user_id)
            db.add(portfolio)
            await db.commit()
            await db.refresh(portfolio)

        return portfolio
