# portfolio/controllers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from portfolio.service import PortfolioService
from core.database import get_session
from users.dependencies import get_current_user

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

@router.get("/me")
async def get_my_portfolio_assets(
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user)
):
    """
    Get all assets in the current user's portfolio.
    """
    return await PortfolioService.get_assets(user.id, db)


@router.post("/me/assets/")
async def add_to_portfolio(
    asset_id: int,
    asset_type: str,
    quantity: float,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user)
):
    """
    Add a new asset to the user's portfolio. The price is fetched from external API automatically.
    """
    return await PortfolioService.add_asset(user.id, asset_id, asset_type, quantity, db)


@router.put("/me/assets/{asset_id}/{asset_type}/")
async def update_portfolio_asset(
    asset_id: int,
    asset_type: str,
    quantity: float,
    price: float,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user)
):
    """
    Update quantity and price for a specific asset in the portfolio.
    """
    success = await PortfolioService.update_asset(user.id, asset_id, asset_type, quantity, price, db)
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found in portfolio.")
    return {"success": True}


@router.delete("/me/assets/{asset_id}/{asset_type}/")
async def remove_from_portfolio(
    asset_id: int,
    asset_type: str,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user)
):
    """
    Remove a specific asset from the user's portfolio.
    """
    success = await PortfolioService.remove_asset(user.id, asset_id, asset_type, db)
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found in portfolio.")
    return {"success": True}
