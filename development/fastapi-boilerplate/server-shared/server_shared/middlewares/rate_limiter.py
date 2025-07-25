"""
Rate limiting middleware using SlowAPI.
"""
from typing import Callable

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request, Response


# Global limiter instance (can use Redis via storage_uri)
limiter = Limiter(key_func=get_remote_address)

def init_rate_limiter(app: FastAPI) -> None:
    """
    Initializes the rate limiter and adds exception handler to the FastAPI app.
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) # type: ignore

def rate_limit_middleware() -> Callable:
    """
    Returns a middleware function to apply global rate limiting.
    """
    async def middleware(request: Request, call_next: Callable) -> Response:
        # Apply a global rate limit (e.g., 5 requests per minute)
        # You can customize this limit string or make it configurable via env
        response = await limiter.limit("5/minute")(call_next)(request)
        return response
    return middleware
