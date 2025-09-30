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

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.client: Optional[AsyncElasticsearch] = None
            self._initialized = True
            logger.info(f"Elasticsearch service initialized for {SERVICE_NAME}")

    async def initialize(self) -> None:
        """Initialize Elasticsearch connection."""
        if self.client is None:
            self.client = AsyncElasticsearch(
                hosts=[app_config.ELASTICSEARCH_URL],
                retry_on_timeout=True,
                max_retries=3
            )
            logger.info(f"Elasticsearch client created for {SERVICE_NAME}")
        
        # Test connection
        await self.health_check()

    async def health_check(self) -> bool:
        """Check Elasticsearch connection health."""
        if not self.client:
            return False
            
        try:
            health = await self.client.cluster.health()
            logger.info(f"Elasticsearch health status: {health['status']}")
            return health['status'] in ['green', 'yellow']
        except ESConnectionError as e:
            logger.error(f"Elasticsearch connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"Elasticsearch health check error: {e}")
            return False

    async def close(self) -> None:
        """Close Elasticsearch connection."""
        if self.client:
            await self.client.close()
            self.client = None
            logger.info(f"Elasticsearch connection closed for {SERVICE_NAME}")

    async def create_index(self, index_name: str, mapping: Optional[dict] = None) -> bool:
        """Create an index with optional mapping."""
        if not self.client:
            logger.error("Elasticsearch client not initialized")
            return False
            
        try:
            if not await self.client.indices.exists(index=index_name):
                if mapping:
                    await self.client.indices.create(index=index_name, body=mapping)
                else:
                    await self.client.indices.create(index=index_name)
                logger.info(f"Index '{index_name}' created successfully")
            else:
                logger.info(f"Index '{index_name}' already exists")
            return True
        except Exception as e:
            logger.error(f"Error creating index '{index_name}': {e}")
            return False

    async def index_document(self, index_name: str, document: dict, doc_id: Optional[str] = None) -> bool:
        """Index a document."""
        if not self.client:
            logger.error("Elasticsearch client not initialized")
            return False
            
        try:
            if doc_id:
                await self.client.index(index=index_name, id=doc_id, body=document)
            else:
                await self.client.index(index=index_name, body=document)
            logger.debug(f"Document indexed in '{index_name}'")
            return True
        except Exception as e:
            logger.error(f"Error indexing document in '{index_name}': {e}")
            return False

    async def search_documents(self, index_name: str, query: dict) -> Optional[dict]:
        """Search documents in an index."""
        if not self.client:
            logger.error("Elasticsearch client not initialized")
            return None
            
        try:
            result = await self.client.search(index=index_name, body=query)
            return result
        except Exception as e:
            logger.error(f"Error searching in '{index_name}': {e}")
            return None


# Global singleton instance
elasticsearch_service = ElasticSearchService()