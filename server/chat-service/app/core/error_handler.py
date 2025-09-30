"""
Error Handlers for the Chat Service.
"""
import traceback
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from server_shared.error import CustomError, AppSystemError, IError
from .exceptions import (
    InsufficientPermission,
    DocumentNotFound,
    MessageNotFound,
    ChatRoomNotFound,
    InvalidMessageContent
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
                    coming_from="application",
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
                coming_from="unknown"
            ).to_dict()
        )
    
    app.add_exception_handler(
        InsufficientPermission,
        simple_handler(
            status.HTTP_401_UNAUTHORIZED,
            "Insufficient permissions",
            error_code="insufficient_permissions"
        )
    )
    app.add_exception_handler(
        DocumentNotFound,
        simple_handler(
            status.HTTP_404_NOT_FOUND,
            "Document not found",
            error_code="document_not_found")
    )
    app.add_exception_handler(
        MessageNotFound,
        simple_handler(
            status.HTTP_404_NOT_FOUND,
            "Message not found",
            error_code="message_not_found")
    )
    app.add_exception_handler(
        ChatRoomNotFound,
        simple_handler(
            status.HTTP_404_NOT_FOUND,
            "Chat room not found",
            error_code="chat_room_not_found")
    )
    app.add_exception_handler(
        InvalidMessageContent,
        simple_handler(
            status.HTTP_400_BAD_REQUEST,
            "Invalid message content",
            error_code="invalid_message_content")
    )