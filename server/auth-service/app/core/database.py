"""
Database connection and session management for the application.
"""
from typing import Union, AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from server_shared.db.DatabaseConnection import SQLModelAsyncDatabaseConnection, DatabaseType
from server_shared.utils.abstract_classes import AbstractAsyncDatabaseConnection

from .config import config
from app.models.user import User

class DatabaseConnection(SQLModelAsyncDatabaseConnection):
    """
    Database connection and session management for the application.
    Inherits from SQLModelAsyncDatabaseConnection to provide async capabilities.
    """

connection_obj: Union[AbstractAsyncDatabaseConnection, None] = None

async def init_db() -> AbstractAsyncDatabaseConnection:
    """
    Create a singleton instance of DatabaseConnection.
    This function ensures that only one instance is created and reused.
    """
    global connection_obj  # [global-statement]
    if connection_obj is not None:
        return connection_obj
    if 'sqlite' in config.DATABASE_URL:
        db_type = DatabaseType.SQLITE
    elif 'postgresql' in config.DATABASE_URL:
        db_type = DatabaseType.POSTGRES
    else:
        db_type = DatabaseType.MYSQL
    if connection_obj is None:
        connection_obj = DatabaseConnection(
            db_uri=config.DATABASE_URL,
            database_type=db_type
        )
    await connection_obj.init_db()
    return connection_obj

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in connection_obj.get_session():
        yield session
