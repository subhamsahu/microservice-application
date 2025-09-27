"""
Database connection and session management for the application.
"""
from typing import Union
from server_shared.utils.abstract_classes import AbstractAsyncDatabaseConnection
from server_shared.db.MongoDbConnection import MongoAsyncDatabaseConnection

from .config import config
from .logger import logger

db: Union[AbstractAsyncDatabaseConnection, None] = None

class DatabaseConnection:
    """
    Database connection and session management for the application.
    """

async def init_db() -> AbstractAsyncDatabaseConnection:
    """
    Create a singleton instance of DatabaseConnection.
    This function ensures that only one instance is created and reused.
    """
    global db
    # Import models lazily to avoid import-time side-effects
    from app.models.catalog import Catalog

    # Create or reuse the MongoDB connection singleton and register Beanie models
    if not db:
        db = MongoAsyncDatabaseConnection(
            db_uri=config.DATABASE_URL,
            database=config.DATABASE,
            document_models=[Catalog],
        )
        await db.connect()
        # init_db will ensure indexes are created
        await db.init_db()

    if await db.health_check_async():
        logger.info(f"Database connected {db}")
    return db

async def disconnect_db() -> None:
    """
    Create a singleton instance of DatabaseConnection.
    This function ensures that only one instance is created and reused.
    """
    global db
    if db:
        await db.disconnect()
        db = None


async def get_db_session():
    """
    Yield a database session for dependency injection.
    """
    # Provide FastAPI dependency that ensures DB is initialized and ready.
    global db
    if not db:
        await init_db()
    # Delegate to the shared connection's get_db dependency (generator)
    if hasattr(db, "get_db"):
        async for _ in db.get_db():
            yield
    else:
        # Fallback: yield control without a session
        yield

async def drop_db() -> None:
    """
    Drop the database.
    """
    global db
    if not db:
        await init_db()
    # Attempt to drop the database via PyMongo client if available
    try:
        if getattr(db, "db", None) is not None:
            await db.db.client.drop_database(db.database_name)  # type: ignore
        elif getattr(db, "client", None) is not None:
            # client is AsyncMongoClient; use sync drop via client[db].client? fall back to blocking call not ideal
            db.client.drop_database(db.database_name)  # type: ignore
    except Exception:
        logger.exception("Failed to drop database")
