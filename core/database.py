# database.py

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Read database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

# Add Base class
class Base(SQLModel):
    """Base class for models"""
    pass

# Create the asynchronous database engine
engine: AsyncEngine = create_async_engine(
    DATABASE_URL, 
    # echo="debug", 
    echo=True,  # Set to False in production for performance
    future=True
)

# Create a sessionmaker for generating sessions
async_session_factory = sessionmaker(
    engine,
    expire_on_commit=False,  # Keeps objects "live" across commits
    class_=AsyncSession  # Uses AsyncSession for asynchronous operation
)

# Function to create tables at application startup
async def create_db_and_tables():
    """
    Create all tables defined in SQLModel metadata.
    This should only be called once during application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# Dependency to get an asynchronous database session
async def get_session() -> AsyncSession:
    """
    Dependency that provides an asynchronous database session.
    Ensures proper cleanup of the session after use.
    """
    async with async_session_factory() as session:
        yield session
