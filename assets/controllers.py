# assets/controllers.py
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_session
from enum import Enum
from assets.services import AssetService
import redis
import os
import json

router = APIRouter(tags=["assets"])

class AssetType(str, Enum):
    stocks = "stocks"
    etfs = "etfs"
    indices = "indices"
    cryptocurrencies = "cryptocurrencies"

@router.get("/sync/{asset_type}")
async def sync_assets_endpoint(
    asset_type: AssetType,  # Use Enum instead of str
    session: AsyncSession = Depends(get_session),
):
    """
    Async endpoint to sync a given asset_type (stocks, etfs, etc.).
    The `asset_type` is now selectable from a dropdown in Swagger UI.
    """
    service = AssetService(session)
    result = await service.sync_assets(asset_type.value)  # `.value` extracts string from Enum
    return result


@router.get("/assets/{asset_type}/symbols", response_model=list[dict[str, str]])
async def get_asset_symbols(
    asset_type: AssetType,
    session: AsyncSession = Depends(get_session),
):
    """
    Get asset symbols from Redis first, if not available then from DB.
    """
    service = AssetService(session)

    # 1. Try getting symbols from Redis
    cached_data = await service.get_asset_symbols_from_redis(asset_type.value)
    if cached_data:
        return cached_data

    # 2. If Redis is empty, fetch from DB
    return await service.get_asset_symbols_from_db(asset_type.value)
