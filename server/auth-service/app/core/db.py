"""
Database connection and session management for the application.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.auth import Auth

from app.core.config import config 

# Create async engine
async_engine: AsyncEngine = create_async_engine(
    config.DATABASE_URL,
    echo=True,  # Optional: shows SQL statements in logs
    future=True
)

# Create sessionmaker globally to avoid re-creating it on each request
async_session_maker = sessionmaker( # type: ignore
    bind=async_engine, # type: ignore
    class_=AsyncSession,
    expire_on_commit=False
)

# Init DB schema
async def init_db() -> None:
    """Initialize the database schema."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# ✅ Yield DB session (for use with FastAPI's Depends)
async def get_session() -> AsyncSession: # type: ignore
    """Yield a database session for dependency injection."""
    async with async_session_maker() as session: # type: ignore
        yield session # type: ignore
