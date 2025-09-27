"""
This module contains the router for the auth API.
"""
from typing import Optional
from fastapi import APIRouter, status, Depends, Query
from app.services.catalog_service import CatalogService
from app.schemas.catalog import CatalogCreateSchema, CatalogResponseSchema, CatalogUpdateSchema
from app.core.logger import logger
from app.core.middlewares import get_current_user

router = APIRouter()

@router.post(
    "/create",
    status_code=status.HTTP_200_OK,
    response_model=CatalogResponseSchema,
    response_description="Catalog Create API",
    tags=["Catalog"],
    operation_id="catalog_create_v1"
)
async def catalog_create_handler(
    catalog_data: CatalogCreateSchema,
    current_user = Depends(get_current_user)
):
    """
    User signup endpoint to register a new user.
    """
    logger.info(f"{current_user=}")
    catalog = await CatalogService.create(catalog_data)
    return catalog

@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    response_description="Search Catalog API",
    operation_id="catalog_search_catalog_v1"
)
async def catalog_search_catalog_handler(
    query: str,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    delivery_time: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None, alias="minPrice"),
    max_price: Optional[int] = Query(None, alias="maxPrice"),
):
    """
    Search endpoint for catalog with limit & offset pagination.
    """
    results = await CatalogService.search(
        query=query,
        limit=limit,
        offset=offset,
        delivery_time=delivery_time,
        min_price=min_price,
        max_price=max_price
    )
    return results

@router.get(
    "/search/category",
    status_code=status.HTTP_200_OK,
    response_description="Search Catalog API",
    operation_id="catalog_search_catalog_by_category_v1"
)
async def catalog_search_catalog_by_category_handler(
    query: str,
):
    """
    Search endpoint for catalog with limit & offset pagination.
    """
    results = await CatalogService.search_catalog_by_category(
        query=query,
    )
    return results

@router.get(
    "/search/more_like/{category_id}",
    status_code=status.HTTP_200_OK,
    response_description="Search Catalog API",
    operation_id="catalog_search_catalog_by_category_v1"
)
async def catalog_search_catalog_more_like_category_handler(
    category_id: str,
):
    """
    Search endpoint for catalog with limit & offset pagination.
    """
    results = await CatalogService.get_more_catalogs_like_this(
        catalog_id=category_id,
    )
    return results

@router.get(
    "/{catalog_id}",
    status_code=status.HTTP_200_OK,
    response_description="Catalog GET API",
    # response_model=CatalogResponseSchema,
    tags=["Catalog"],
    operation_id="catalog_get_by_id_v1"
)
async def catalog_get_document_by_id_handler(
    catalog_id: str,
    current_user = Depends(get_current_user)
):
    """
    User signup endpoint to register a new user.
    """
    logger.info(f"{current_user=}")
    catalog = await CatalogService.get_by_id(catalog_id)
    return catalog

@router.delete(
    "/{catalog_id}",
    status_code=status.HTTP_200_OK,
    response_description="Catalog Delete API",
    tags=["Catalog"],
    operation_id="catalog_delete_v1"
)
async def catalog_delete_handler(
    catalog_id: str,
    current_user = Depends(get_current_user)
):
    """
    User signup endpoint to register a new user.
    """
    logger.info(f"{current_user=}")
    message = await CatalogService.delete(catalog_id)
    return message

@router.put(
    "/{catalog_id}",
    status_code=status.HTTP_200_OK,
    response_description="Catalog Update API",
    response_model=CatalogResponseSchema,
    tags=["Catalog"],
    operation_id="catalog_update_v1"
)
async def catalog_update_handler(
    catalog_id: str,
    catalog_data: CatalogUpdateSchema,
    current_user = Depends(get_current_user)
):
    """
    User signup endpoint to register a new user.
    """
    logger.info(f"{current_user=}")
    message = await CatalogService.update(catalog_id, catalog_data)
    return message
