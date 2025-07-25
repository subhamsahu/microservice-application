"""
This module defines custom exceptions for the application.
"""

class AppException(Exception):
    """
    AppExceptionCase is the base exception class for the application.
    """

class ServerStartError(AppException):
    """
    Exception raised when the server fails to start.
    """

class DatabaseInitializeError(AppException):
    """
    Exception raised when the server fails to start.
    """
