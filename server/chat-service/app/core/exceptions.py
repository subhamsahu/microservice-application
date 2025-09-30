"""
This module defines custom exception classes for the chat service.
All exceptions inherit from AppException and represent specific error cases
such as invalid tokens, user not found, insufficient permissions, and more.
"""
from server_shared.error import AppException

class ServerStartError(AppException):
    """Raised when the server fails to start."""

class DatabaseInitializeError(AppException):
    """Raised when the database initialization fails."""

class InsufficientPermission(AppException):
    """Raised when a user does not have sufficient permissions for an action."""

class DocumentNotFound(AppException):
    """Raised when a document is not found."""

class MessageNotFound(AppException):
    """Raised when a message is not found."""

class ChatRoomNotFound(AppException):
    """Raised when a chat room is not found."""

class InvalidMessageContent(AppException):
    """Raised when message content is invalid."""