"""
This module contains the router for the users API.
"""
from typing import Optional
from fastapi import APIRouter, status, Depends, Query
from fastapi.responses import JSONResponse

from app.core.logger import logger
from app.services.catalog_service import CatalogService


router = APIRouter()
catalog_service= CatalogService()

@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    response_description="Search Catalog API",
    operation_id="auth_search_catalog_v1"
)
async def auth_search_catalog_handler(
    query: str,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    delivery_time: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None, alias="minPrice"),
    max_price: Optional[int] = Query(None, alias="maxPrice"),
) -> JSONResponse:
    """
    Search endpoint for catalog with limit & offset pagination.
    """
    results = await catalog_service.search(
        query=query,
        limit=limit,
        offset=offset,
        delivery_time=delivery_time,
        min_price=min_price,
        max_price=max_price
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=results
    )


@router.get(
    "/{catalog_id}",
    status_code=status.HTTP_200_OK,
    operation_id="auth_get_catalog_by_id"
)
async def auth_get_catalog_by_id_handler(
    catalog_id: str,
):
    """
    Catalog endpoint to get catalog by id.
    """
    catalog = await catalog_service.get_document_by_id(catalog_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=catalog
    )
