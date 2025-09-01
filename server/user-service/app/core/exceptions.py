"""
This module defines custom exception classes for the authentication service.
All exceptions inherit from AppException and represent specific error cases
such as invalid tokens, user not found, insufficient permissions, and more.
"""
from server_shared.error import AppException

class ServerStartError(AppException):
    """Raised when the server fails to start."""
class DatabaseInitializeError(AppException):
    """Raised when the database initialization fails."""
class InvalidToken(AppException):
    """Raised when a provided token is invalid."""
class RevokedToken(AppException):
    """Raised when a token has been revoked."""
class AccessTokenRequired(AppException):
    """Raised when an access token is required but missing."""
class RefreshTokenRequired(AppException):
    """Raised when a refresh token is required but missing."""
class UserAlreadyExists(AppException):
    """Raised when attempting to create a user that already exists."""
class InvalidCredentials(AppException):
    """Raised when user credentials are invalid during authentication."""
class InsufficientPermission(AppException):
    """Raised when a user does not have sufficient permissions for an action."""
class UserNotFound(AppException):
    """Raised when a user is not found in the system."""

class AccountNotVerified(AppException):
    """Raised when a user's account has not been verified."""
class DocumentNotFound(AppException):
    """Raised when a document is not found."""
