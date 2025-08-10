from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from server_shared.middlewares.gateway_middleware import verify_gateway_request

class GatewayMiddleware(BaseHTTPMiddleware):
    """
    Gateway Middleware for services to check if request is coming from gateway service
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        await verify_gateway_request(request)
        response = await call_next(request)
        return response
