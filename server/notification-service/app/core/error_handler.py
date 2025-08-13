"""
Error Handlers for the Notification Service.
"""
import traceback
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from server_shared.error import CustomError, AppSystemError, IError
from .exceptions import (
    EmailSendingError,
    MessageQueueError,
    TemplateNotFound,
    InvalidEmailAddress,
    EmailServiceUnavailable,
    RabbitMQConnectionError,
    NotificationNotFound,
    InvalidNotificationData
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
                    coming_from="notification",
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
                coming_from="notification"
            ).to_dict()
        )

    # Notification-specific exception handlers
    app.add_exception_handler(
        EmailSendingError,
        simple_handler(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to send email",
            error_code="email_send_failed",
            resolution="Please try again later or contact administrator"
        )
    )

    app.add_exception_handler(
        MessageQueueError,
        simple_handler(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Message queue service unavailable",
            error_code="queue_service_error",
            resolution="Please try again later"
        )
    )

    app.add_exception_handler(
        TemplateNotFound,
        simple_handler(
            status.HTTP_404_NOT_FOUND,
            "Email template not found",
            error_code="template_not_found"
        )
    )

    app.add_exception_handler(
        InvalidEmailAddress,
        simple_handler(
            status.HTTP_400_BAD_REQUEST,
            "Invalid email address provided",
            error_code="invalid_email",
            resolution="Please provide a valid email address"
        )
    )

    app.add_exception_handler(
        EmailServiceUnavailable,
        simple_handler(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Email service is currently unavailable",
            error_code="email_service_down",
            resolution="Please try again later"
        )
    )

    app.add_exception_handler(
        RabbitMQConnectionError,
        simple_handler(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Unable to connect to message queue",
            error_code="rabbitmq_connection_error",
            resolution="Please check message queue service"
        )
    )

    app.add_exception_handler(
        NotificationNotFound,
        simple_handler(
            status.HTTP_404_NOT_FOUND,
            "Notification not found",
            error_code="notification_not_found"
        )
    )

    app.add_exception_handler(
        InvalidNotificationData,
        simple_handler(
            status.HTTP_400_BAD_REQUEST,
            "Invalid notification data provided",
            error_code="invalid_notification_data",
            resolution="Please check the notification data format"
        )
    )
