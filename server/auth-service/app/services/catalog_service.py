"""
This module contains the user service for handling user-related operations.
"""
from typing import Optional
from fastapi import Depends

from app.services.elasticsearch import ElasticSearchService
from app.core.constants import ELASTIC_SEARCH_INDEXES
from app.core.logger import logger
from app.core.exceptions import DocumentNotFound

class CatalogService:
    """
    This service handles catalog search operations.
    """

    def __init__(self):
        self.elastic_search_service =  ElasticSearchService()

    async def get_document_by_id(self,doc_id: str):
        """
        Get a document by its ID.
        """
        document = await self.elastic_search_service.get_document_by_id(ELASTIC_SEARCH_INDEXES.CATALOG, doc_id)
        if not document:
            raise DocumentNotFound("Document not found")
        return document



    async def search(
        self,
        query: str,
        limit: int,
        offset: int,
        delivery_time: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None
    ):
        """
        Elasticsearch search endpoint.
        """
        query_list = [
            {
                "query_string": {
                    "fields": [
                        "username",
                        "title",
                        "description",
                        "basicDescription",
                        "basicTitle",
                        "categories",
                        "subCategories",
                        "tags"
                    ],
                    "query": f"*{query}*"
                }
            },
            {"term": {"active": True}}
        ]

        if delivery_time:
            query_list.append({
                "query_string": {
                    "fields": ["expectedDelivery"],
                    "query": f"*{delivery_time}*"
                }
            })

        if min_price is not None and max_price is not None:
            query_list.append({
                "range": {
                    "price": {"gte": min_price, "lte": max_price}
                }
            })

        search_body = {
            "index": f"{ELASTIC_SEARCH_INDEXES.CATALOG}",
            "from": offset,   # offset instead of search_after
            "size": limit,    # limit instead of fixed page size
            "query": {"bool": {"must": query_list}},
            "sort": [
                {"sortId": "asc"}  # simple sort, can be customized
            ]
        }

        result = await self.elastic_search_service.search(**search_body)
        total = result["hits"]["total"]["value"]
        hits = [hit["_source"] for hit in result["hits"]["hits"]]

        return {
            "message": "Search catalog results",
            "total": total,
            "catalog": hits
        }
