"""
Module for buyer-related operations.
"""
from typing import Optional, Dict, Any
from bson import ObjectId
from beanie import PydanticObjectId

from fastapi.encoders import jsonable_encoder

from app.core.exceptions import DocumentNotFound
from app.core.constants import ELASTIC_SEARCH_INDEXES
from app.schemas.catalog import CatalogCreateSchema, CatalogResponseSchema, CatalogUpdateSchema, CatalogESSchema
from app.models.catalog import Catalog
from app.core.logger import logger
from app.services.rabbitmq.connection import create_rabbitmq_channel
from app.services.rabbitmq.producer import publish_message_to_queue
from app.services.elasticsearch import elasticsearch_service
from app.services.redis import redis_service


class CatalogService:
    """Service class for catalog-related operations."""


    @staticmethod
    async def get_by_id(catalog_id: str) -> Dict[str, Any]:
        """Create Catalog"""
        document = await elasticsearch_service.get_document_by_id(
            index=ELASTIC_SEARCH_INDEXES.CATALOG,
            doc_id=str(catalog_id),  # ensure string
        )
        if document is None:
            raise DocumentNotFound(f"Catalog with id {catalog_id} not found")
        logger.info(f"Catalog Data is {document}")
        return document

    @staticmethod
    async def create(catalog_data: CatalogCreateSchema) -> Dict[str, Any]:
        """Create Catalog"""
        exchange_name = "msa-seller-update"
        routing_key = "user-seller"
        document_count = await elasticsearch_service.count_document(ELASTIC_SEARCH_INDEXES.CATALOG)
        logger.info(f"{document_count=}")
        catalog = Catalog(**catalog_data.model_dump())
        catalog.sort_id = document_count + 1
        await catalog.insert()
        catalog_channel = await create_rabbitmq_channel()
        # Failure Scenerio Here, handle if publish fails on elastic search insert fails
        if catalog_channel is not None:
            await publish_message_to_queue(
                channel=catalog_channel,
                exchange_name=exchange_name,
                routing_key=routing_key,
                message={
                    "update_data": {
                        "seller_id": catalog.seller_id,
                        "count": 1
                    },
                    "event": "update-catalog-count",
                    "from": "catalog_service"
                }
            )
        else:
            logger.error(
                "Error in getting rabbitmq connection, Seller Update Count is not updated")
        # Insert the document into elastic search
        elastic_data = jsonable_encoder(CatalogESSchema(**catalog.model_dump()))
        logger.info(f"{elastic_data=}")
        await elasticsearch_service.create_document(
            index=ELASTIC_SEARCH_INDEXES.CATALOG,
            doc_id=str(catalog.id),  # ensure string
            body=elastic_data
        )
        return catalog.model_dump()
    
    @staticmethod
    async def delete(catalog_id: str) -> Dict[str, Any]:
        """Create Catalog"""
        exchange_name = "msa-seller-update"
        routing_key = "user-seller"
        catalog = await Catalog.get(PydanticObjectId(catalog_id))
        if not catalog:
            raise DocumentNotFound(f"Document with id {catalog_id} not found")
        await catalog.delete()
        catalog_channel = await create_rabbitmq_channel()
        # Failure Scenerio Here, handle if publish fails on elastic search insert fails
        if catalog_channel is not None:
            await publish_message_to_queue(
                channel=catalog_channel,
                exchange_name=exchange_name,
                routing_key=routing_key,
                message={
                    "update_data": {
                        "seller_id": catalog.seller_id,
                        "count": -1
                    },
                    "event": "update-catalog-count",
                    "from": "catalog_service"
                }
            )
        else:
            logger.error(
                "Error in getting rabbitmq connection, Seller Update Count is not updated")
        # Insert the document into elastic search
        elastic_data = jsonable_encoder(CatalogResponseSchema(**catalog.model_dump()))
        logger.info(f"{elastic_data=}")
        await elasticsearch_service.delete_document(
            index=ELASTIC_SEARCH_INDEXES.CATALOG,
            doc_id=str(catalog.id),  # ensure string
        )
        return {"message": "Catalog deleted successfully"}
    
    @staticmethod
    async def update(catalog_id: str, catalog_data:CatalogUpdateSchema) -> Dict[str, Any]:
        """Update Catalog"""
        catalog = await Catalog.get(PydanticObjectId(catalog_id))
        if not catalog:
            raise DocumentNotFound(f"Document with id {catalog_id} not found")
        # Update only provided fields
        update_data = catalog_data.model_dump(exclude_unset=True, by_alias=True)
        for field, value in update_data.items():
            setattr(catalog, field, value)

        await catalog.save()
        logger.info(f"catalog with id {catalog_id} updated")
        # Update the document into elastic search
        elastic_data = jsonable_encoder(CatalogESSchema(**catalog.model_dump()))
        logger.info(f"{elastic_data=}")
        await elasticsearch_service.create_document(
            index=ELASTIC_SEARCH_INDEXES.CATALOG,
            doc_id=str(catalog.id),  # ensure string
            body=elastic_data
        )
        return catalog.model_dump()
    

    @staticmethod
    async def update_category_review(catalog_id: str, rating:int) -> None:
        """
        Update review stats for a seller.
        Expected data: {
            "category_id": str,
            "rating": int (1-5)
        }
        """
        rating_types = {
            "1": "one",
            "2": "two",
            "3": "three",
            "4": "four",
            "5": "five",
        }
        rating_key = rating_types[str(rating)]

        result = await Catalog.find_one(Catalog.id == PydanticObjectId(catalog_id)).update(
            {
                "$inc": {
                    "ratings_count": 1,
                    "rating_sum": rating,
                    f"rating_categories.{rating_key}.value": rating,
                    f"rating_categories.{rating_key}.count": 1,
                }
            }
        )
        if result.modified_count == 0:
            logger.warning(f"No Catalog updated for review with ID {catalog_id}")
            
    @staticmethod
    async def get_user_selected_catalog_category(key: str) -> str:
        """Fetch user-selected catalog category from Redis."""
        value = await redis_service.get(key)
        return value or ""
    
    @staticmethod
    async def search(
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

        result = await elasticsearch_service.search(**search_body)
        total = result["hits"]["total"]["value"]
        hits = [hit["_source"] for hit in result["hits"]["hits"]]

        return {
            "message": "Search catalog results",
            "total": total,
            "catalog": hits
        }
    
    @staticmethod
    async def search_catalog_by_category(query: str,) -> Dict[str, Any]:
        """search catalog by category"""
        result = await elasticsearch_service.search(
            index=f"{ELASTIC_SEARCH_INDEXES.CATALOG}",
            size=10,
            query={
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "fields": ["categories"],
                                "query": f"*{query}*"
                            }
                        },
                        {
                            "term": {
                                "active": True
                            }
                        }
                    ]
                }
            },
        )

        total = result["hits"]["total"]["value"]
        hits = result["hits"]["hits"]

        return {
            "total": total,
            "hits": hits
        }
    
    @staticmethod
    async def get_more_catalogs_like_this(catalog_id: str) -> Dict[str, Any]:
        """
        Fetch catalogs similar to the given catalog ID using Elasticsearch's more_like_this query.
        https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-mlt-query
        """
        result = await elasticsearch_service.search(
            index=f"{ELASTIC_SEARCH_INDEXES.CATALOG}",
            size=5,
            query={
                "more_like_this": {
                    "fields": [
                        "username",
                        "title",
                        "description",
                        "basicDescription",
                        "basicTitle",
                        "categories",
                        "subCategories",
                        "tags",
                    ],
                    "like": [
                        {
                            "_index": "catalogs",
                            "_id": catalog_id
                        }
                    ],
                }
            },
        )

        total = result["hits"]["total"]["value"]
        hits = result["hits"]["hits"]

        return {
            "total": total,
            "hits": hits
        }
