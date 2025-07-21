"""
Middleware for FastAPI application to limit request body size.

This middleware checks the size of the request body and 
raises an HTTP 413 error if it exceeds the specified limit.
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class BodySizeLimiterMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit the size of request bodies.
    """
    def __init__(self, app, max_body_size: int):
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next):
        body = await request.body()
        if len(body) > self.max_body_size:
            raise HTTPException(status_code=413, detail="Request body too large")
        return await call_next(request)
