"""
Database connection and session management for the application.
"""
from typing import Union, AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from server_shared.db.DatabaseConnection import SQLModelAsyncDatabaseConnection, DatabaseType
from server_shared.utils.abstract_classes import AbstractAsyncDatabaseConnection

from .config import config
from app.models.user import User

connection_obj: Union[AbstractAsyncDatabaseConnection, None] = None
class DatabaseConnection(SQLModelAsyncDatabaseConnection):
    """
    Database connection and session management for the application.
    Inherits from SQLModelAsyncDatabaseConnection to provide async capabilities.
    """

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
    """
    Yield a database session for dependency injection.
    """
    async for session in connection_obj.get_session():
        yield session


async def drop_db() -> None:
    """
    Drop the database.
    """
    from urllib.parse import urlparse, unquote
    import asyncpg
    import asyncmy
    from sqlalchemy.engine import make_url
    from app.core.config import config as app_config

    db_uri = app_config.DATABASE_URL

    async def __drop_postgres_database(db_uri):
        """
        Connects to the default 'postgres' DB and drops the target database.
        """
        parsed = urlparse(db_uri.replace("postgresql+asyncpg://", "postgresql://"))
        user = parsed.username
        password = parsed.password
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        target_db = parsed.path.lstrip("/")
        user = unquote(user) if user else None
        password = unquote(password) if password else None

        conn = await asyncpg.connect(
            user=user,
            password=password,
            database="postgres",
            host=host,
            port=port
        )
        try:
            await conn.execute(f'DROP DATABASE IF EXISTS "{target_db}"')
            print(f"Database '{target_db}' dropped.")
        finally:
            await conn.close()

    async def __drop_mysql_database(db_uri):
        """
        Connects to the MySQL server and drops the target database.
        """
        parsed = urlparse(db_uri.replace("mysql+asyncmy://", "mysql://"))
        user = parsed.username
        password = parsed.password
        host = parsed.hostname or "localhost"
        port = parsed.port or 3306
        target_db = parsed.path.lstrip("/")

        conn = await asyncmy.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            autocommit=True
        )
        try:
            async with conn.cursor() as cur:
                await cur.execute(f"DROP DATABASE IF EXISTS `{target_db}`;")
                print(f"MySQL DB '{target_db}' dropped.")
        finally:
            conn.close()

    def get_database_type(db_uri: str) -> DatabaseType:
        url = make_url(db_uri)
        driver = url.drivername.lower()

        if "postgresql" in driver:
            return DatabaseType.POSTGRES
        elif "mysql" in driver:
            return DatabaseType.MYSQL
        elif "sqlite" in driver:
            return DatabaseType.SQLITE
        else:
            raise ValueError(f"Unsupported database type in URI: {driver}")

    database_type = get_database_type(db_uri)

    if database_type in DatabaseType.POSTGRES:
        await __drop_postgres_database(db_uri)
    elif database_type in DatabaseType.MYSQL:
        await __drop_mysql_database(db_uri)
    elif database_type in DatabaseType.SQLITE:
        print("SQLite database is a file, please remove it manually.")
