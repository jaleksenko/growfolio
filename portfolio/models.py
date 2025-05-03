# portfolio/models.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import UniqueConstraint


class Portfolio(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    user: "User" = Relationship(back_populates="portfolios", sa_relationship_kwargs={"lazy": "joined"})
    assets: list["PortfolioAsset"] = Relationship(back_populates="portfolio")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.created_at = self.created_at or datetime.utcnow()
        self.updated_at = self.updated_at or datetime.utcnow()


class PortfolioAsset(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    portfolio_id: int = Field(foreign_key="portfolio.id", nullable=False)
    asset_id: int = Field(nullable=False)
    asset_type: str = Field(nullable=False)
    quantity: float = Field(default=0.0)
    purchase_price: float = Field(default=0.0)
    added_at: datetime | None = None

    portfolio: "Portfolio" = Relationship(back_populates="assets")

    __table_args__ = (
        UniqueConstraint("portfolio_id", "asset_id", "asset_type", name="unique_portfolio_asset"),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.added_at = self.added_at or datetime.utcnow()
