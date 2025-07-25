"""
This module contains decorators used in the application.
"""

from functools import wraps
import traceback
import inspect
import logging
import asyncio
from typing import Any, Callable, Coroutine, Dict

def singleton(class_):
    """
    A decorator that implements the Singleton design pattern.

    This decorator ensures that a class has only one instance and provides a global
    point of access to it. It is used to decorate a class, and any subsequent
    instantiations of that class will return the same instance.

    Args:
        class_ (type): The class to be decorated as a singleton.

    Returns:
        function: A wrapper function that returns the singleton instance of the class.
    """

    _instances = {}
    @wraps(class_)
    def wrapper(*args, **kwargs):
        if class_ not in _instances:
            _instances[class_] = class_(*args, **kwargs)
        return _instances[class_]
    return wrapper



def detailed_error_logger(func: Callable) -> Callable:
    """
    Decorator to log detailed error information for both synchronous and asynchronous functions.
    """
    @wraps(func)
    def sync_wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (ValueError, TypeError, KeyError) as e:
            return log_exception(self, func, args, kwargs, e)
        except Exception as e:
            # Optionally log unexpected exceptions separately
            return log_exception(self, func, args, kwargs, e)

    @wraps(func)
    async def async_wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except (ValueError, TypeError, KeyError) as e:
            return log_exception(self, func, args, kwargs, e)
        except Exception as e:
            return log_exception(self, func, args, kwargs, e)

    def log_exception(self, func, args, kwargs, e) -> Dict[str, Any]:
        tb = traceback.extract_tb(e.__traceback__)[-1]
        filename = tb.filename
        line_no = tb.lineno

        error_details = {
            "service": "Agent Server",
            "function": func.__name__,
            "file": filename,
            "line": line_no,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
            "arguments": {
                "args": [repr(arg) for arg in args],
                "kwargs": {k: repr(v) for k, v in kwargs.items()}
            }
        }

        self.logger.error("Detailed Error Log", extra=error_details)

        self.logger.error(
            f"[{error_details['service']}] Exception in {error_details['function']} "
            f"({error_details['file']}:{error_details['line']})\n"
            f"Type: {error_details['error_type']}\n"
            f"Message: {error_details['error_message']}\n"
            f"Args: {error_details['arguments']['args']}\n"
            f"Kwargs: {error_details['arguments']['kwargs']}\n"
            f"Traceback:\n{error_details['traceback']}"
        )

        return {"error": error_details["error_message"]}

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
