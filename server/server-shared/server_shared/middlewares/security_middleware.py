"""
Security middlewares: HPP protection and secure headers.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from secure import Secure

secure_headers = Secure.with_default_headers()


class PreventHPPMiddleware(BaseHTTPMiddleware):
    """
    Middleware to prevent HTTP Parameter Pollution (HPP)
    by removing duplicate query parameters.
    Similar to the HPP protection in Express.js.
    """
    async def dispatch(self, request: Request, call_next):
        request.scope["query_string"] = b"&".join(
            sorted(set(request.scope["query_string"].split(b"&")))
        )
        response = await call_next(request)
        return response


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add secure HTTP headers (helmet-like).
    Similar to the Helmet.js middleware in Express.js.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        await secure_headers.set_headers_async(response) # type: ignore
        # Add CSP to support Swagger UI (adjust as needed)
        csp = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
            "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
        )
        response.headers["Content-Security-Policy"] = csp

        return response
