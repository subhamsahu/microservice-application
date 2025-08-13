"""
This module defines custom error classes for handling various HTTP errors in a web application.
It includes classes for bad requests, not found errors, unauthorized access,
file too large errors, and server errors.
Each class inherits from a base `CustomError` class and provides a method to serialize the error
into a dictionary format suitable for API responses."""

from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    HTTP_503_SERVICE_UNAVAILABLE
)

class IError:
    """
    Represents an error response object with a message, status code, status,
    and the component that the error originated from.
    """

    def __init__(self, message: str, status_code: int, status: str, coming_from: str, **extra):
        self.message = message
        self.status_code = status_code
        self.status = status
        self.coming_from = coming_from
        self.extra = extra

    def to_dict(self) -> dict:
        """
        Serializes the error details into a dictionary format.
        This method is useful for returning error responses in a consistent format."""
        data = {
            "message": self.message,
            "statusCode": self.status_code,
            "status": self.status,
            "comingFrom": self.coming_from
        }
        if self.extra:
            data.update(self.extra)
        return data
    
class AppException(Exception):
    """Base exception for the application."""

class CustomError(AppException):
    """
    Represents a custom error that extends the base `Exception` class.
    This abstract class provides a common interface for handling custom errors
    in the application.
    """
    status_code: int
    status: str = "error"
    coming_from: str

    def __init__(self, message: str, coming_from: str, **extra):
        super().__init__(message)
        self.message = message
        self.coming_from = coming_from
        self.extra = extra

    def serialize_errors(self) -> dict:
        """
        Serializes the error details into a dictionary format.
        """
        return IError(
            message=self.message,
            status_code=self.status_code,
            status=self.status,
            coming_from=self.coming_from,
            **self.extra
        ).to_dict()

class BadRequestError(CustomError):
    """
    Represents a 400 Bad Request error.
    """
    status_code = HTTP_400_BAD_REQUEST

class NotFoundError(CustomError):
    """
    Represents a 404 Not Found error.
    """
    status_code = HTTP_404_NOT_FOUND

class NotAuthorizedError(CustomError):
    """
    Represents a 401 Unauthorized error.
    """
    status_code = HTTP_401_UNAUTHORIZED

class FileTooLargeError(CustomError):
    """
    Represents a 413 Payload Too Large error.
    """
    status_code = HTTP_413_REQUEST_ENTITY_TOO_LARGE

class ServerError(CustomError):
    """
    Represents a 503 Service Unavailable error.
    """
    status_code = HTTP_503_SERVICE_UNAVAILABLE

class AppSystemError(Exception):
    """
    Represents an error object with additional properties for handling
    system-level errors. This class extends the built-in `Exception` type
    and adds optional properties for capturing the error code, file path,
    system call, and stack trace.
    """

    def __init__(self, message: str, errno=None, code=None, path=None, syscall=None, stack=None):
        super().__init__(message)
        self.errno = errno
        self.code = code
        self.path = path
        self.syscall = syscall
        self.stack = stack
