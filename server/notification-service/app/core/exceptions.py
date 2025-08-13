"""
This module defines custom exception classes for the notification service.
All exceptions inherit from AppException and represent specific error cases
such as email sending failures, message queue issues, and more.
"""
from server_shared.error import AppException

class ServerStartError(AppException):
    """Raised when the server fails to start."""

class DatabaseInitializeError(AppException):
    """Raised when the database initialization fails."""

class EmailSendingError(AppException):
    """Raised when email sending fails."""

class MessageQueueError(AppException):
    """Raised when message queue operations fail."""

class TemplateNotFound(AppException):
    """Raised when email template is not found."""

class InvalidEmailAddress(AppException):
    """Raised when email address is invalid."""

class EmailServiceUnavailable(AppException):
    """Raised when email service is unavailable."""

class RabbitMQConnectionError(AppException):
    """Raised when RabbitMQ connection fails."""

class NotificationNotFound(AppException):
    """Raised when notification record is not found."""

class InvalidNotificationData(AppException):
    """Raised when notification data is invalid."""
