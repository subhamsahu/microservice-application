"""
This module contains abstract base classes to be used in the application for 
database connections and operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AbstractDatabaseConnection(ABC):
    """
    Abstract base class for database connections.
    """
    @abstractmethod
    async def connect(self) -> Any:
        """
        Establishes a connection to the database.
        Raises:
            ConnectionError: If the connection fails.
        """

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Closes the connection to the database.
        Raises:
            ConnectionError: If the disconnection fails.
        """

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Checks if the connection is established.
        Returns:
            bool: True if connected, False otherwise.
        """


class AbstractDatabaseManager(ABC):
    """
    Abstract base class for database operations.
    """

    def __init__(self, db: Any):
        self.db = db

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> int:
        """
        Creates a new record in the database.
        Args:
            data (Dict[str, Any]): The data for the new record.
        Returns:
            int: The ID of the created record.
        Raises:
            ValueError: If the data is invalid.
        """

    @abstractmethod
    def read(self, record_id: str) -> Dict[str, Any]:
        """
        Reads a record from the database by its ID.
        Args:
            record_id (str): The ID of the record to read.
        Returns:
            Dict[str, Any]: The record data.
        Raises:
            KeyError: If the record does not exist.
        """

    @abstractmethod
    def update(self, record_id: str, data: Dict[str, Any]) -> None:
        """
        Updates a record in the database by its ID.
        Args:
            record_id (str): The ID of the record to update.
            data (Dict[str, Any]): The new data for the record.
        Raises:
            KeyError: If the record does not exist.
            ValueError: If the data is invalid.
        """

    @abstractmethod
    def delete(self, record_id: str) -> None:
        """
        Deletes a record from the database by its ID.
        Args:
            record_id (str): The ID of the record to delete.
        Raises:
            KeyError: If the record does not exist.
        """

    @abstractmethod
    def list(self) -> List[Dict[str, Any]]:
        """
        Lists all records in the database.
        Returns:
            List[Dict[str, Any]]: A list of all records.
        """


class ServerFacade(ABC):
    """
    Abstract base class for server operations
    """
    @abstractmethod
    def initialize_server(self):
        """
        Initializes the server.
        """

    @abstractmethod
    def start_server(self):
        """
        Starts the server.
        """
