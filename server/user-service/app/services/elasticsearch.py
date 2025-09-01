"""
Elasticsearch client configuration and connection check.
Singleton implementation for centralized connection management.
"""

# standard library imports
from time import sleep
import asyncio
from typing import Optional

# third-party imports
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError as ESConnectionError, NotFoundError

# private imports
from app.core.logger import logger
from app.core.config import config as app_config
from app.core.constants import SERVICE_NAME
from server_shared.utils.meta_classes import Singleton


class ElasticSearchException(Exception):
    """Exception class for Elasticsearch-related errors."""


class ElasticSearchService(metaclass=Singleton):
    """
    Singleton Elasticsearch service for centralized connection management.
    """

    def __init__(self, url: str = app_config.ELASTICSEARCH_URL):
        """
        Initializes the Elasticsearch client as singleton.
        :param url: URL of the Elasticsearch instance.
        """
        if not hasattr(self, '_initialized'):
            self._client: Optional[AsyncElasticsearch] = None
            self._url = url
            self._initialized = True
            self._connected = False

    @property
    def client(self) -> Optional[AsyncElasticsearch]:
        """Get the ElasticSearch client instance."""
        return self._client

    async def initialize(self) -> bool:
        """Initialize the ElasticSearch connection."""
        if self._client is not None:
            return self._connected
            
        try:
            self._client = AsyncElasticsearch(self._url)
            await self.check_connection()
            self._connected = True
            return True
        except Exception as error:
            logger.error(f"Failed to initialize Elasticsearch: {error}")
            self._connected = False
            return False

    async def check_connection(self) -> None:
        """
        Continuously checks the health of the Elasticsearch cluster until a successful connection is made.
        Logs the status after successful connection or error messages on failure.
        """
        if not self._client:
            raise ElasticSearchException("ElasticSearch client not initialized")
            
        is_connected = False
        retry_count = 0
        max_retries = 5
        
        while not is_connected and retry_count < max_retries:
            try:
                health = await self._client.cluster.health()
                logger.info(
                    f"{SERVICE_NAME.capitalize()} Elasticsearch health status - {health['status']}")
                is_connected = True
                self._connected = True
            except ESConnectionError as error:
                retry_count += 1
                logger.error(f"Connection to Elasticsearch failed (attempt {retry_count}/{max_retries}). Retrying...")
                logger.error(f"{SERVICE_NAME} check_connection() method: {error}")
                if retry_count < max_retries:
                    await asyncio.sleep(3)  # Backoff before retrying
                else:
                    raise ElasticSearchException(f"Failed to connect to Elasticsearch after {max_retries} attempts")

    async def close(self):
        """Close the client connection."""
        if self._client:
            try:
                await self._client.close()
                logger.info("ElasticSearch connection closed.")
                self._connected = False
            except Exception as error:
                logger.error(f"Error closing ElasticSearch connection: {error}")
            finally:
                self._client = None


# Global singleton instance
elasticsearch_service = ElasticSearchService()
