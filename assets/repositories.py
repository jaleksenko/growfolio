# assets/repositories.py
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from typing import List, Dict, Any

import csv
import io
import logging

logger = logging.getLogger(__name__)

    
class AssetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def sync_assets_with_api(
            self,
            asset_model: SQLModel,
            api_data: list[dict],
            asset_type: str
        ) -> dict:
            """
            Synchronizes asset data (stocks, ETFs, indices, cryptocurrencies) with PostgreSQL.
            
            Now inserts each record **individually** instead of bulk inserting.
            Ensures cryptocurrencies are processed correctly.
            Deletes outdated records **at the end** for consistency.
            """

            logger.info(f"🔄 Starting sync for {asset_type}...")

            # 1️. Fetch all existing records from the database
            db_assets_result = await self.session.execute(select(asset_model))
            db_assets_rows = db_assets_result.scalars().all()

            # Create a mapping of existing assets (symbol, exchange) → asset object
            db_assets_map = {(row.symbol, row.exchange): row for row in db_assets_rows}

            # 2️. Process incoming API data
            api_assets_keys = set()
            inserted_count = 0

            for item in api_data:
                symbol = item.get("symbol")
                exchange = item.get("exchange")

                if asset_type == "cryptocurrencies":
                    # Process cryptocurrencies with (symbol, exchange) as unique key
                    currency_base = item.get("currency_base")
                    currency_quote = item.get("currency_quote")

                    if not symbol or not currency_base or not currency_quote or not exchange:
                        logger.warning(f"⚠️ Skipping cryptocurrency due to missing data: {item}")
                        continue  

                    key = (symbol, exchange)
                    api_assets_keys.add(key)

                    if key in db_assets_map:
                        continue  # Skip existing cryptos

                    # Insert record one by one
                    new_crypto = asset_model(
                        symbol=symbol, exchange=exchange,
                        currency_base=currency_base, currency_quote=currency_quote
                    )

                else:
                    # Process stocks, ETFs, indices
                    name = item.get("name")
                    currency = item.get("currency")

                    if not symbol or not exchange or not name or not currency:
                        logger.warning(f"⚠️ Skipping asset due to missing data: {item}")
                        continue  

                    key = (symbol, exchange)
                    api_assets_keys.add(key)

                    if key in db_assets_map:
                        continue  # Skip existing assets

                    # Insert record one by one
                    new_crypto = asset_model(
                        symbol=symbol, exchange=exchange, name=name, currency=currency
                    )

                try:
                    self.session.add(new_crypto)
                    await self.session.commit()
                    inserted_count += 1
                except IntegrityError:
                    logger.error(f"❌ Duplicate insert error: {symbol} on {exchange}")
                    await self.session.rollback()
            
            # 3️.  Identify and delete outdated records
            db_assets_keys = set(db_assets_map.keys())
            keys_to_delete = db_assets_keys - api_assets_keys

            if keys_to_delete:
                try:
                    symbols_to_delete = [key[0] for key in keys_to_delete]
                    await self.session.execute(
                        delete(asset_model).where(asset_model.symbol.in_(symbols_to_delete))
                    )
                    await self.session.commit()
                    logger.info(f"🗑️ Removed {len(keys_to_delete)} outdated records from {asset_type}.")
                except Exception as e:
                    logger.error(f"❌ Error while deleting records in {asset_type}: {e}")
                    await self.session.rollback()

            return {
                "inserted": inserted_count,
                "removed": len(keys_to_delete)
            }