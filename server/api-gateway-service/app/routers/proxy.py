import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from app.core.logger import logger
from app.core.exceptions import AppException
from app.utils.security import create_gateway_token
from app.core.config import config
from app.core.dependency import get_current_user, AccessTokenBearer

router = APIRouter()

methods: list[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]


def create_route_handler(http_method: str):
    """
    Creates a route handler for the specified HTTP method."""
    async def route_handler(service: str, path: str, request: Request):
        return await proxy_handler(service, path, request, http_method)
    return route_handler


for method in methods:
    router.add_api_route(
        "/{service}/{path:path}",
        create_route_handler(method),  # bind method
        methods=[method],
        include_in_schema=True,
    )


async def proxy_handler(service: str, path: str, request: Request, http_method: str):
    """
    Proxies requests to the specified service and path.
    """
    # Below is the service map, currently taking from .env, implement service discovery here
    service_maps = {
        "auth": {
            "base_url": f"{config.AUTH_BASE_URL}/api/v1/auth",
            "public_routes": [
                "signup",
                "signin",
                "resend/email",
                "verify/email",
                "forgot/password",
                "reset/password",
                "catalog"
            ]
        },
        "buyer": {
            "base_url": f"{config.USERS_BASE_URL}/api/v1/buyer",
            "public_routes": [
            ]
        },  
        "seller": {
            "base_url": f"{config.USERS_BASE_URL}/api/v1/seller",
            "public_routes": [
            ]
        }, 
        "catalog": {
            "base_url": f"{config.CATALOG_BASE_URL}/api/v1/catalog",
            "public_routes": [
            ]
        }  
    }

    service_map = service_maps.get(service)
    if not service_map:
        return JSONResponse(status_code=404, content={"error": f"Unknown service {service}"})
    base_url = service_map.get("base_url") if service_map else None
    public_paths = service_map.get("public_routes", [])
    logger.info(f"Public paths: {public_paths}")
    current_user = None
    if not any(path.startswith(pub) for pub in public_paths):
        # ✅ Manually run token validation and attach user
        token_bearer = AccessTokenBearer()
        token_details: dict = await token_bearer(request)
        current_user = token_details.get("user")
        logger.info(f"Authenticated user: {current_user}")
    query_params = request.url.query
    target_url = f"{base_url}/{path}"
    if query_params:
        target_url += f"?{query_params}"

    body = await request.body()
    logger.info(f"{http_method} {target_url}")
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    headers['gatewaytoken'] = create_gateway_token(service, current_user)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=http_method,
                url=target_url,
                headers=headers,
                content=body,
            )

        excluded_headers = {"content-encoding",
                            "transfer-encoding", "connection"}
        response_headers = {
            k: v for k, v in response.headers.items() if k.lower() not in excluded_headers
        }

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers,
        )

    except httpx.RequestError as e:
        logger.error(f"Proxy error: {str(e)}")
        return JSONResponse(status_code=502, content={"error": str(e)})
