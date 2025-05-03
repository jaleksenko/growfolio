from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from watchlist.services import WatchlistService
from watchlist.models import Watchlist, WatchlistResponse, WatchlistAssetResponse
from core.database import get_session
from users.dependencies import get_current_user

router = APIRouter(prefix="/watchlists", tags=["watchlists"])


# ✅ Fetch or create the user's default watchlist
@router.get("/me/", response_model=WatchlistResponse)
async def get_default_watchlist(
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user)
):
    """
    Retrieve the user's default watchlist.  
    If no watchlist exists, one will be created automatically.
    """
    watchlist = await WatchlistService.get_or_create_default_watchlist(user.id, db)
    return watchlist


# ✅ Fetch all assets in the user's default watchlist
@router.get("/me/assets/", response_model=list[WatchlistAssetResponse])
async def get_watchlist_assets(
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user)
):
    """
    Retrieve all assets from the user's default watchlist.
    Ensures that the watchlist is a valid object before accessing assets.
    """
    watchlist = await WatchlistService.get_or_create_default_watchlist(user.id, db)

    # Ensure watchlist is an instance of Watchlist, not a dictionary
    if not isinstance(watchlist, Watchlist):
        raise HTTPException(status_code=500, detail="Invalid watchlist object retrieved.")

    assets = await WatchlistService.get_watchlist_assets(user.id, db)

    # ✅ Ensure assets are returned as Pydantic models
    if assets and isinstance(assets[0], dict):  
        return [WatchlistAssetResponse(**asset) for asset in assets]  # Convert dicts to Pydantic models
    return assets if assets else []

# ✅ Add an asset to the user's default watchlist
@router.post("/me/assets/", response_model=WatchlistAssetResponse)
async def add_asset_to_watchlist(
    asset_id: int,
    asset_type: str,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user)
):
    """
    Add an asset (stock, ETF, crypto) to the user's default watchlist.
    If the asset already exists, return it instead of adding a duplicate.
    """
    new_asset = await WatchlistService.add_asset_to_watchlist(user.id, asset_id, asset_type, db)

    if new_asset:
        return new_asset  # ✅ Return the asset without duplication
    else:
        raise HTTPException(status_code=400, detail="Asset already exists in the watchlist.")



# ✅ Remove an asset from the user's default watchlist
@router.delete("/me/assets/{asset_id}/{asset_type}/", response_model=bool)
async def remove_asset_from_watchlist(
    asset_id: int,
    asset_type: str,  # ✅ Include asset type in request
    db: AsyncSession = Depends(get_session),
    user=Depends(get_current_user)
):
    """
    Remove a specific asset from the user's default watchlist.
    """
    success = await WatchlistService.remove_asset_from_watchlist(user.id, asset_id, asset_type, db)
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found in watchlist.")
    return success

