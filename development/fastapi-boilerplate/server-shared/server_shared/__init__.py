"""
:Description: Entry point for server_shared package. 
 Exposes core utilities for logging, middleware, and cloud operations.
:Author: Shubham Sahu
:Version: 1.0
"""

from .logger import Logger
from .utils.helpers.string_utils import StringUtils
from .utils.formatters import display_dotted_string
from .middlewares.gateway_middleware import verify_gateway_request

__all__ = [
    "Logger",
    "StringUtils",
    "display_dotted_string",
    "verify_gateway_request"
]
