# assets/models.py
from sqlmodel import SQLModel, Field, Relationship, Column, Integer
from sqlalchemy.types import String, JSON
from sqlalchemy import UniqueConstraint
from typing import List, Optional
from pydantic import BaseModel


# BASE MODEL (Shared Fields)
class BaseAsset(SQLModel, table=False):
    """
    A common base for all asset tables, providing:
      - An auto-increment ID (primary key)
      - Shared columns like `name`
      - Not a real table (table=False), meaning it won't create a table itself.
    """
    id: int | None = Field(default=None, primary_key=True)  # ✅ ID only here!
    name: str = Field(nullable=False)
    
# STOCK MODEL
class Stock(BaseAsset, table=True):  # ✅ Inherit from BaseAsset
    """
    Stock class
    """
    symbol: str = Field(index=True, nullable=False)
    exchange: str = Field(index=True, nullable=False)  # Now required
    currency: str | None = None

    __table_args__ = (
        UniqueConstraint("symbol", "exchange", name="unique_stock"),
    )

# ETF MODEL
class ETF(BaseAsset, table=True):  # ✅ Inherit from BaseAsset
    """
    ETF class
    """
    symbol: str = Field(index=True, nullable=False)
    exchange: str = Field(index=True, nullable=False)  # Now required
    currency: str | None = None

    __table_args__ = (
        UniqueConstraint("symbol", "exchange", name="unique_etf"),
    )


# INDEX MODEL
class Index(BaseAsset, table=True):  # ✅ Inherit from BaseAsset
    """
    Indices class
    """
    symbol: str = Field(index=True, nullable=False)
    exchange: str = Field(index=True, nullable=False)
    currency: str | None = None


    __table_args__ = (
        UniqueConstraint("symbol", "exchange", name="unique_index"),
    )


# CRYPTOCURRENCY MODEL
class Cryptocurrency(SQLModel, table=True): 
    """
    Cryptocurrencies class
    """
    id: int | None = Field(default=None, primary_key=True)
    symbol: str = Field(index=True, nullable=False)
    exchange: str = Field(index=True, nullable=False)
    currency_base: str | None = None
    currency_quote: str | None = None

    __table_args__ = (
        UniqueConstraint("symbol", "exchange", name="unique_cryptocurrency"),
    )


# RESPONSE MODELS FOR API
class AssetFullInfo(SQLModel):
    """
    Full asset information response model.
    """
    symbol: str
    name: str
    currency: str | None = None
    exchange: str | None = None
    country: str | None = None
    type: str | None = None
    currency_base: str | None = None
    currency_quote: str | None = None

    class Config:
        from_attributes = True


class AssetSymbolName(SQLModel):
    """
    Symbol and name only for quick lookups.
    """
    symbol: str
    name: str

    class Config:
        from_attributes = True


class CryptocurrencyFullInfo(SQLModel):
    """
    Cryptocurrency-specific response model.
    """
    symbol: str
    exchange: str | None = None
    currency_base: str | None = None
    currency_quote: str | None = None

    class Config:
        from_attributes = True


class CryptocurrencySymbolOnly(SQLModel):
    """
    Only return the symbol for cryptocurrency queries.
    """
    symbol: str

    class Config:
        from_attributes = True