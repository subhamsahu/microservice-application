"""
Error Handlers for the API Gateway Service.
"""
import traceback
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from server_shared.error import CustomError, AppSystemError, IError
from .exceptions import (
    InvalidToken,
    RevokedToken,
    AccessTokenRequired,
    RefreshTokenRequired,
    ServiceUnavailable,
    ProxyError,
    RouteNotFound,
    GatewayTimeoutError,
    RateLimitExceeded,
    InvalidGatewayToken,
    ServiceAuthenticationError
)
from .logger import logger


def register_all_errors(app: FastAPI):
    """
    Registers all custom and generic error handlers in one place.
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "body": exc.body},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # Handle 404 separately
        if exc.status_code == 404:
            full_url = str(request.url)
            logger.error(f"{full_url} endpoint does not exist.")
            return JSONResponse(
                status_code=404,
                content={"message": "The endpoint called does not exist."}
            )

        # General HTTPException handler
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(CustomError)
    async def custom_error_handler(request: Request, exc: CustomError):
        logger.error(
            f"[CustomError] {exc.coming_from} - {exc.message} | Path: {request.url.path}")
        return JSONResponse(status_code=exc.status_code, content=exc.serialize_errors())

    @app.exception_handler(AppSystemError)
    async def system_error_handler(_: Request, exc: AppSystemError):
        logger.error(
            f"[AppSystemError] {exc} | Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content=IError(
                message=str(exc),
                status_code=500,
                status="error",
                coming_from="system",
                errno=exc.errno,
                code=exc.code,
                path=exc.path,
                syscall=exc.syscall,
                stack=exc.stack
            ).to_dict()
        )

    def simple_handler(status_code: int, message: str, **extra):
        async def handler(_: Request, exc: Exception):
            logger.error(f"[{exc.__class__.__name__}] {message}")
            return JSONResponse(
                status_code=status_code,
                content=IError(
                    message=message,
                    status_code=status_code,
                    status="error",
                    coming_from="gateway",
                    **extra
                ).to_dict()
            )
        return handler

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception):
        logger.error(
            f"[UnhandledError] {exc} | Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content=IError(
                message="An unexpected error occurred",
                status_code=500,
                status="error",
                coming_from="gateway"
            ).to_dict()
        )

    # Gateway-specific exception handlers
    app.add_exception_handler(
        InvalidToken,
        simple_handler(
            status.HTTP_401_UNAUTHORIZED,
            "Token is invalid or expired",
            resolution="Please get new token",
            error_code="invalid_token"
        )
    )

    app.add_exception_handler(
        RevokedToken,
        simple_handler(
            status.HTTP_401_UNAUTHORIZED,
            "Token is invalid or revoked",
            resolution="Please get new token",
            error_code="token_revoked"
        )
    )

    app.add_exception_handler(
        AccessTokenRequired,
        simple_handler(
            status.HTTP_401_UNAUTHORIZED,
            "Please provide a valid access token",
            resolution="Get an access token",
            error_code="access_token_required"
        )
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        simple_handler(
            status.HTTP_403_FORBIDDEN,
            "Please provide a valid refresh token",
            resolution="Get a refresh token",
            error_code="refresh_token_required"
        )
    )

    app.add_exception_handler(
        ServiceUnavailable,
        simple_handler(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Downstream service is currently unavailable",
            error_code="service_unavailable",
            resolution="Please try again later"
        )
    )

    app.add_exception_handler(
        ProxyError,
        simple_handler(
            status.HTTP_502_BAD_GATEWAY,
            "Failed to proxy request to downstream service",
            error_code="proxy_error",
            resolution="Please try again or contact administrator"
        )
    )

    app.add_exception_handler(
        RouteNotFound,
        simple_handler(
            status.HTTP_404_NOT_FOUND,
            "Route not found in gateway",
            error_code="route_not_found"
        )
    )

    app.add_exception_handler(
        GatewayTimeoutError,
        simple_handler(
            status.HTTP_504_GATEWAY_TIMEOUT,
            "Gateway timeout occurred",
            error_code="gateway_timeout",
            resolution="Please try again later"
        )
    )

    app.add_exception_handler(
        RateLimitExceeded,
        simple_handler(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Rate limit exceeded",
            error_code="rate_limit_exceeded",
            resolution="Please wait before making more requests"
        )
    )

    app.add_exception_handler(
        InvalidGatewayToken,
        simple_handler(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid gateway token",
            error_code="invalid_gateway_token",
            resolution="Please contact administrator"
        )
    )

    app.add_exception_handler(
        ServiceAuthenticationError,
        simple_handler(
            status.HTTP_401_UNAUTHORIZED,
            "Service authentication failed",
            error_code="service_auth_failed",
            resolution="Please check service credentials"
        )
    )
