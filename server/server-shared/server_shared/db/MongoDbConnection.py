"""
Generic Database Manager for MongoDB using Beanie ODM (PyMongo Async API).
"""

from typing import Optional, List, AsyncGenerator
from beanie import init_beanie, Document
from pymongo import AsyncMongoClient  # ✅ Use PyMongo Async API

from ..utils.abstract_classes import AbstractAsyncDatabaseConnection
from ..utils.meta_classes import Singleton


class BaseMeta(Singleton, type(AbstractAsyncDatabaseConnection)):
    """
    Metaclass combining Singleton and AbstractDatabaseConnection metaclasses.
    """


class MongoAsyncDatabaseConnection(AbstractAsyncDatabaseConnection, metaclass=BaseMeta):
    """
    Singleton class for managing MongoDB async connections using Beanie ODM.
    """

    def __init__(
        self,
        *,
        host: str = "localhost",
        port: int = 27017,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: str = "test_db",
        db_uri: Optional[str] = None,
        document_models: Optional[List[type[Document]]] = None,
    ):
        """
        Initialize MongoDB connection parameters.
        """
        if not db_uri:
            if username and password:
                self.db_uri = f"mongodb://{username}:{password}@{host}:{port}/{database}"
            else:
                self.db_uri = f"mongodb://{host}:{port}/{database}"
        else:
            self.db_uri = db_uri

        self.database_name = database
        self.client: Optional[AsyncMongoClient] = None
        self.db = None
        self.document_models = document_models or []
        self._initialized = False

    async def connect(self):
        """
        Establish MongoDB connection and initialize Beanie.
        """
        if self.client:
            return self.client

        print(f"Connecting to MongoDB: {self.db_uri}")
        self.client = AsyncMongoClient(self.db_uri)  # ✅ PyMongo Async
        self.db = self.client[self.database_name]

        if self.document_models:
            await init_beanie(database=self.db, document_models=self.document_models)

        self._initialized = True
        return self.client

    async def init_db(self):
        """
        Initialize MongoDB with registered Beanie models (ensures indexes).
        """
        if not self.client:
            await self.connect()

        if self.document_models:
            await init_beanie(database=self.db, document_models=self.document_models)
            print("MongoDB initialized with Beanie models.")

    async def is_connected(self) -> bool:
        """
        Check if the connection is active by pinging MongoDB.
        """
        if not self.client:
            return False
        try:
            await self.db.command("ping")  # ✅ PyMongo async style
            return True
        except Exception:
            return False

    async def health_check_async(self) -> bool:
        """
        Perform a health check (alias for is_connected).
        """
        return await self.is_connected()

    async def disconnect(self):
        """
        Disconnect from MongoDB and clean up resources.
        """
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB.")
            self.client = None
            self.db = None
            self._initialized = False

    async def get_db(self) -> AsyncGenerator[None, None]:
        """
        FastAPI dependency to ensure DB connection is ready.
        Yields control without returning a session object (MongoDB is sessionless by default).
        """
        if not self._initialized:
            await self.connect()
            await self.init_db()
        try:
            yield
        finally:
            # In Mongo we don't close per-request, just keep client alive
            pass
