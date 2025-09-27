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

    async def index_exists(self, index_name: str) -> bool:
        """Check if an index exists."""
        if not self._client:
            logger.error("ElasticSearch client not initialized")
            return False
            
        try:
            return bool(await self._client.indices.exists(index=index_name))
        except ElasticSearchException as e:
            logger.error(f"{e}")
            return False

    async def create_index(self, index_name: str, mappings: dict | None = None) -> None:
        """Create an index if it does not exist."""
        if not self._client:
            logger.error("ElasticSearch client not initialized")
            return
            
        if await self.index_exists(index_name):
            logger.info(f'Index "{index_name}" already exists.')
            return
        try:
            await self._client.indices.create(index=index_name, mappings=mappings or {})
            logger.info(f"Created index: {index_name}")
        except ElasticSearchException as e:
            logger.error(f"Error creating index {index_name}")
            logger.error(f"{e}")

    async def get_document_by_id(self, index: str, doc_id: str) -> dict | None:
        """Retrieve a document by its ID."""
        if not self._client:
            logger.error("ElasticSearch client not initialized")
            return None
            
        try:
            doc = await self._client.get(index=index, id=doc_id)
            return doc["_source"] if doc.get("found", True) else None
        except NotFoundError:
            logger.warning(f"Document {doc_id} not found in index {index}")
            return None
        except ElasticSearchException as e:
            logger.error("Error fetching document by ID")
            logger.error(f"{e}")
            return None

    async def create_document(self, index: str, doc_id: str, body: dict) -> None:
        """Create or replace a document."""
        if not self._client:
            logger.error("ElasticSearch client not initialized")
            return
            
        try:
            await self._client.index(index=index, id=doc_id, document=body)
            logger.info(f"Document {doc_id} indexed in {index}")
        except ElasticSearchException as e:
            logger.error(f"Error indexing document {doc_id}")
            logger.error(f"{e}")

    async def update_document(self, index: str, doc_id: str, body: dict) -> None:
        """
        Update an existing document by ID.
        Uses Elasticsearch's partial update (_update API).
        :param index: Index name.
        :param doc_id: Document ID.
        :param body: Partial document body (fields to update).
        """
        if not self._client:
            logger.error("ElasticSearch client not initialized")
            return

        try:
            await self._client.update(index=index, id=doc_id, body={"doc": body})
            logger.info(f"Document {doc_id} updated in {index}")
        except NotFoundError:
            logger.warning(f"Document {doc_id} not found in {index}, cannot update")
        except ElasticSearchException as e:
            logger.error(f"Error updating document {doc_id}")
            logger.error(f"{e}")


    async def delete_document(self, index: str, doc_id: str) -> None:
        """Delete a document by its ID."""
        if not self._client:
            logger.error("ElasticSearch client not initialized")
            return
            
        try:
            await self._client.delete(index=index, id=doc_id)
            logger.info(f"Document {doc_id} deleted from {index}")
        except NotFoundError:
            logger.warning(f"Document {doc_id} not found in {index}")
        except ElasticSearchException as e:
            logger.error(f"Error deleting document {doc_id}")
            logger.error(f"{e}")

    async def count_document(self, index: str) -> int:
        """Delete a document by its ID."""
        doc_count = 0
        if not self._client:
            logger.error("ElasticSearch client not initialized")
            return doc_count
            
        try:
            response = await self._client.count(index=index)
            doc_count = response["count"]
            logger.info(f"Documents count: {doc_count} from index: {index}")
        except NotFoundError:
            logger.warning(f"Document {doc_count} not found in {index}")
        except ElasticSearchException as e:
            logger.error(f"Error deleting document {doc_count}")
            logger.error(f"{e}")
        return doc_count

    async def search(self, **kwargs) -> dict:
        """
        Perform a search on Elasticsearch with auto-scaling pagination.
        """
        if not self._client:
            logger.error("ElasticSearch client not initialized")
            return {"hits": {"total": {"value": 0}, "hits": []}, "next_sort": None}
            
        try:
            offset = kwargs.pop("from", 0)
            size = kwargs.get("size", 10)
            sort = kwargs.get("sort", [{"_id": "asc"}])  # default sort

            if offset > 5000:
                # Deep pagination mode (search_after)
                pages_to_skip = offset // size
                last_sort = None
                temp_result = None

                for _ in range(pages_to_skip):
                    temp_result = await self._client.search(
                        **({**kwargs, "size": size, "sort": sort, "search_after": last_sort}
                        if last_sort else
                        {**kwargs, "size": size, "sort": sort})
                    )
                    temp_data = temp_result.body  # convert to dict
                    if not temp_data["hits"]["hits"]:
                        break
                    last_sort = temp_data["hits"]["hits"][-1]["sort"]

                # Final batch
                result_obj = await self._client.search(
                    **({**kwargs, "size": size, "sort": sort, "search_after": last_sort}
                    if last_sort else
                    {**kwargs, "size": size, "sort": sort})
                )
            else:
                # Normal pagination mode
                result_obj = await self._client.search(**{**kwargs, "from": offset, "size": size})

            # Convert ObjectApiResponse → dict
            result = result_obj.body

            # Include next_sort token
            if result["hits"]["hits"]:
                result["next_sort"] = result["hits"]["hits"][-1].get("sort")
            else:
                result["next_sort"] = None

            return result

        except ElasticSearchException as e:
            logger.error(f"Error searching index: {kwargs.get('index')}")
            logger.error(f"{e}")
            return {"hits": {"total": {"value": 0}, "hits": []}, "next_sort": None}

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
