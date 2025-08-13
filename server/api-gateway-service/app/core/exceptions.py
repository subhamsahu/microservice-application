"""
This module defines custom exception classes for the API Gateway service.
All exceptions inherit from AppException and represent specific error cases
such as service unavailability, routing failures, and authentication issues.
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

class ServiceUnavailable(AppException):
    """Raised when a downstream service is unavailable."""

class ProxyError(AppException):
    """Raised when proxy request fails."""

class RouteNotFound(AppException):
    """Raised when a route is not found."""

class GatewayTimeoutError(AppException):
    """Raised when gateway timeout occurs."""

class RateLimitExceeded(AppException):
    """Raised when rate limit is exceeded."""

class InvalidGatewayToken(AppException):
    """Raised when gateway token is invalid."""

class ServiceAuthenticationError(AppException):
    """Raised when service authentication fails."""
