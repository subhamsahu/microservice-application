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

class InvalidToken(AppException):
    """User has provided an invalid or expired token"""


class RevokedToken(AppException):
    """User has provided a token that has been revoked"""
class AccessTokenRequired(AppException):
    """User has provided a refresh token when an access token is needed"""

class RefreshTokenRequired(AppException):
    """User has provided an access token when a refresh token is needed"""
