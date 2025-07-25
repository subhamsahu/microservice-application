import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from app.core.logger import AppLogger
from app.core.exceptions import AppException

router = APIRouter()
logger = AppLogger()

methods: list[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

def create_route_handler(method: str):
    """
    Creates a route handler for the specified HTTP method."""
    async def route_handler(service: str, path: str, request: Request):
        return await proxy_handler(service, path, request, method)
    return route_handler

for method in methods:
    router.add_api_route(
        "/{service}/{path:path}",
        create_route_handler(method),  # bind method
        methods=[method],
        include_in_schema=True,
    )

async def proxy_handler(service: str, path: str, request: Request, method: str):
    """
    Proxies requests to the specified service and path.
    """
    service_map = {
        "auth": "https://jsonplaceholder.typicode.com",
        "user": "http://localhost:4003",
    }

    base_url = service_map.get(service)
    if not base_url:
        return JSONResponse(status_code=404, content={"error": "Unknown service"})

    query_params = request.url.query
    target_url = f"{base_url}/{path}"
    if query_params:
        target_url += f"?{query_params}"

    body = await request.body()
    logger.info(f"[API Gateway] {method} {target_url}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=target_url,
                headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
                content=body,
            )

        excluded_headers = {"content-encoding", "transfer-encoding", "connection"}
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
