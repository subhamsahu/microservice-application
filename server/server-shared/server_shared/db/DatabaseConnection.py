"""
Generic Database Manager for SQLModel supporting PostgreSQL, MySQL, and SQLite.
"""

from enum import Enum
from typing import Optional, AsyncGenerator
from urllib.parse import urlparse, unquote

import asyncpg
import asyncmy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from ..utils.abstract_classes import AbstractAsyncDatabaseConnection
from ..utils.meta_classes import Singleton


class BaseMeta(Singleton, type(AbstractAsyncDatabaseConnection)):
    """
    Metaclass combining Singleton and AbstractDatabaseConnection metaclasses.
    """


class DatabaseType(str, Enum):
    """
    Enum for supported databases.
    """
    POSTGRES = "postgresql+asyncpg"
    MYSQL = "mysql+asyncmy"
    SQLITE = "sqlite+aiosqlite"

    def __str__(self):
        return self.value


class SQLModelAsyncDatabaseConnection(AbstractAsyncDatabaseConnection):
    """
    Singleton class for managing SQL database async connections using SQLModel.
    """

    def __init__(
        self,
        *,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        db_uri: Optional[str] = None,
        database_type: DatabaseType = DatabaseType.POSTGRES
    ):
        if not db_uri and database_type != DatabaseType.SQLITE:
            if not (host and port and username and password and database):
                raise ValueError("Either db_uri or all connection details must be provided.")

        self.database_type = database_type
        self.engine: Optional[AsyncEngine] = None
        self.session_maker: Optional[sessionmaker] = None

        if db_uri:
            self.db_uri = db_uri
        else:
            self.db_uri = self._build_uri(
                database_type=database_type,
                host=host,
                port=port,
                username=username,
                password=password,
                database=database
            )

    def _build_uri(
        self,
        database_type: DatabaseType,
        host: Optional[str],
        port: Optional[int],
        username: Optional[str],
        password: Optional[str],
        database: Optional[str],
    ) -> str:
        if database_type == DatabaseType.SQLITE:
            return f"sqlite+aiosqlite:///{database or 'app.db'}"
        return f"{database_type}://{username}:{password}@{host}:{port}/{database}"

    async def __create_postgres_database_if_not_exists(self):
        """
        Connects to the default 'postgres' DB and creates the target database if it doesn't exist.
        `db_url` should be in format: postgresql+asyncpg://user:pass@host:port/dbname
        """

        # Remove the driver scheme prefix (`+asyncpg`)
        parsed = urlparse(self.db_uri.replace("postgresql+asyncpg://", "postgresql://"))

        user = parsed.username
        password = parsed.password
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        target_db = parsed.path.lstrip("/")  # removes leading slash
        user = unquote(user) if user else None
        password = unquote(password) if password else None

        # Connect to the default 'postgres' database
        conn = await asyncpg.connect(
            user=user,
            password=password,
            database="postgres",
            host=host,
            port=port
        )

        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", target_db
        )
        if not exists:
            await conn.execute(f'CREATE DATABASE "{target_db}"')
            print(f"Database '{target_db}' created.")
        else:
            print(f"Database '{target_db}' already exists.")

        await conn.close()

    async def __create_mysql_database_if_not_exists(self):
        """
        Connects to the MySQL server and creates the target database if it doesn't exist.
        """
        # Remove the driver scheme prefix (`+asyncmy`)
        parsed = urlparse(self.db_uri.replace("mysql+asyncmy://", "mysql://"))
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

        async with conn.cursor() as cur:
            await cur.execute(f"CREATE DATABASE IF NOT EXISTS `{target_db}`;")
            print(f"MySQL DB '{target_db}' ensured.")
        conn.close()


    async def connect(self) -> AsyncEngine:
        """
        Asynchronously create engine and sessionmaker.
        """
        if self.engine:
            return self.engine

        print(f"Connecting to DB: {self.db_uri}")
        self.engine = create_async_engine(
            self.db_uri,
            echo=True,
            future=True,
            pool_pre_ping=True
        )
        self.session_maker = sessionmaker( # type: ignore
            bind=self.engine, # type: ignore
            class_=AsyncSession,
            expire_on_commit=False
        )
        return self.engine

    async def init_db(self) -> None:
        """
        Initialize schema using SQLModel metadata.
        """
        if self.database_type == DatabaseType.POSTGRES:
            await self.__create_postgres_database_if_not_exists()
        elif self.database_type == DatabaseType.MYSQL:
            await self.__create_mysql_database_if_not_exists()
        elif self.database_type == DatabaseType.SQLITE:
            # SQLite does not require database creation, just ensure the file exists
            if not self.db_uri.endswith('.db'):
                raise ValueError("SQLite DB URI must end with '.db'")
        if not self.engine:
            await self.connect()
        try:
            async with self.engine.begin() as conn: # type: ignore
                await conn.run_sync(SQLModel.metadata.create_all)
            print("Database schema initialized.")
        except Exception as exc:
            print("Failed to initialize schema.")
            raise Exception(f"Error initializing database schema: {exc}") from exc

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Yield an async session (for FastAPI Depends).
        """
        if not self.session_maker:
            await self.connect()

        async with self.session_maker() as session: # type: ignore
            yield session

    def is_connected(self) -> bool:
        return self.engine is not None

    async def health_check_async(self) -> bool:
        """
        Perform a health check to verify the connection is active."""
        if not self.engine:
            await self.connect()
        try:
            async with self.engine.connect() as conn: # type: ignore
                # Execute a simple query to check connection
                await conn.execute("SELECT 1") # type: ignore
            return True
        except SQLAlchemyError:
            return False

    async def disconnect(self):
        """
        disconnect from the database and clean up resources.
        """
        if self.engine:
            try:
                await self.engine.dispose()
                print("Disconnected from DB.")
                self.engine = None
                self.session_maker = None
            except SQLAlchemyError as e:
                print(f"Failed to disconnect: {e}")
