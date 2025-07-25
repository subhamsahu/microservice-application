"""
This module contains a metaclasses used in the application
"""

from threading import Lock

class Singleton(type):
    """
    A metaclass that implements the Singleton design pattern.

    This metaclass ensures that only one instance of a class is created,
    and provides a global point of access to it.
    """
    _instances = {}
    _lock: Lock = Lock()  # Ensures thread safety for Singleton
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
