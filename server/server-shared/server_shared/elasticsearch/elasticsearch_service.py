"""
Elasticsearch client configuration and connection check.
"""

# standard library imports
import asyncio
import logging

# third-party imports
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError as ESConnectionError, NotFoundError


class ElasticSearchException(Exception):
    """Exception class for Elasticsearch-related errors."""


class ElasticSearchService:
    """
    A class to manage Elasticsearch connection and health check.
    """

    def __init__(self, url: str):
        """
        Initializes the Elasticsearch client.
        :param url: URL of the Elasticsearch instance.
        """
        self.client: AsyncElasticsearch = AsyncElasticsearch(url)

    async def check_connection(self) -> None:
        """
        Continuously checks the health of the Elasticsearch cluster until a successful connection is made.
        Logs the status after successful connection or error messages on failure.
        """
        is_connected = False
        while not is_connected:
            try:
                health = await self.client.cluster.health()
                logging.info(f"Elasticsearch health status - {health['status']}")
                is_connected = True
            except ESConnectionError as error:
                logging.error("Connection to Elasticsearch failed. Retrying...")
                logging.error(f"check_connection() method: {error}")
                await asyncio.sleep(3)  # Backoff before retrying

    async def index_exists(self, index_name: str) -> bool:
        """Check if an index exists."""
        try:
            return bool(await self.client.indices.exists(index=index_name))
        except ElasticSearchException as e:
            logging.error(f"{e}")
            return False

    async def create_index(self, index_name: str, mappings: dict | None = None) -> None:
        """Create an index if it does not exist."""
        if await self.index_exists(index_name):
            logging.info(f"Index '{index_name}' already exists.")
            return
        try:
            await self.client.indices.create(index=index_name, mappings=mappings or {})
            logging.info(f"Created index: {index_name}")
        except ElasticSearchException as e:
            logging.error(f"Error creating index {index_name}: {e}")

    async def get_document_by_id(self, index: str, doc_id: str) -> dict | None:
        """Retrieve a document by its ID."""
        try:
            doc = await self.client.get(index=index, id=doc_id)
            return doc["_source"] if doc.get("found", True) else None
        except NotFoundError:
            logging.warning(f"Document '{doc_id}' not found in index '{index}'")
            return None
        except ElasticSearchException as e:
            logging.error(f"Error fetching document by ID: {e}")
            return None

    async def create_document(self, index: str, doc_id: str, body: dict) -> None:
        """Create or replace a document."""
        try:
            await self.client.index(index=index, id=doc_id, document=body)
            logging.info(f"Document '{doc_id}' indexed in '{index}'")
        except ElasticSearchException as e:
            logging.error(f"Error indexing document '{doc_id}': {e}")

    async def delete_document(self, index: str, doc_id: str) -> None:
        """Delete a document by its ID."""
        try:
            await self.client.delete(index=index, id=doc_id)
            logging.info(f"Document '{doc_id}' deleted from '{index}'")
        except NotFoundError:
            logging.warning(f"Document '{doc_id}' not found in '{index}'")
        except ElasticSearchException as e:
            logging.error(f"Error deleting document '{doc_id}': {e}")

    async def search(self, **kwargs) -> dict:
        """
        Perform a search on Elasticsearch with auto-scaling pagination.
        """
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
                    temp_result = await self.client.search(
                        **({**kwargs, "size": size, "sort": sort, "search_after": last_sort}
                        if last_sort else
                        {**kwargs, "size": size, "sort": sort})
                    )
                    temp_data = temp_result.body  # convert to dict
                    if not temp_data["hits"]["hits"]:
                        break
                    last_sort = temp_data["hits"]["hits"][-1]["sort"]

                # Final batch
                result_obj = await self.client.search(
                    **({**kwargs, "size": size, "sort": sort, "search_after": last_sort}
                    if last_sort else
                    {**kwargs, "size": size, "sort": sort})
                )
            else:
                # Normal pagination mode
                result_obj = await self.client.search(**{**kwargs, "from": offset, "size": size})

            # Convert ObjectApiResponse → dict
            result = result_obj.body

            # Include next_sort token
            if result["hits"]["hits"]:
                result["next_sort"] = result["hits"]["hits"][-1].get("sort")
            else:
                result["next_sort"] = None

            return result

        except ElasticSearchException as e:
            logging.error(f"Error searching index '{kwargs.get('index')}': {e}")
            return {"hits": {"total": {"value": 0}, "hits": []}, "next_sort": None}



    async def close(self):
        """Close the client connection."""
        await self.client.close()
