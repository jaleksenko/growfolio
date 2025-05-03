from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import UniqueConstraint

# Base model Watchlist
class Watchlist(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    created_at: datetime | None = None
    updated_at: datetime | None = None


    # Define connections
    user: "User" = Relationship(back_populates="watchlists", sa_relationship_kwargs={"lazy": "joined"})
    assets: list["WatchlistAsset"] = Relationship(back_populates="watchlist", sa_relationship_kwargs={"lazy": "selectin"})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


# Assets model in Watchlist
class WatchlistAsset(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    watchlist_id: int = Field(foreign_key="watchlist.id", nullable=False)
    asset_id: int = Field(nullable=False)
    asset_type: str = Field(nullable=False)
    added_at: datetime | None = None

    # ✅ Enforce uniqueness at the database level
    __table_args__ = (UniqueConstraint("watchlist_id", "asset_id", "asset_type", name="unique_watchlist_asset"),)

    watchlist: "Watchlist" = Relationship(back_populates="assets", sa_relationship_kwargs={"lazy": "joined"})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.added_at is None:
            self.added_at = datetime.utcnow()


# Pydentic Models
class WatchlistResponse(BaseModel):
    id: int
    name: str
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WatchlistAssetResponse(BaseModel):
    id: int
    asset_id: int
    asset_type: str
    symbol: str | None = None 
    name: str | None = None
    exchange: str | None = None
    currency: str | None = None
    group: str | None = None
    currency_base: str | None = None
    currency_quote: str | None = None
    added_at: datetime

    model_config = {"from_attributes": True}
