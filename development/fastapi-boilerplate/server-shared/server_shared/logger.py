"""
:Description:   ECS-compatible logger with console, file, and Elasticsearch support.
:Author:        Shubham Sahu
:Version:       2.0
"""

# local imports
import logging
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from threading import Lock
from typing import Dict, Optional

# third-party imports
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import (ConnectionError as ESConnectionError,
                                    TransportError as ESTransportError)


class LoggerSingletonMeta(type):
    """
    Thread-safe implementation of Singleton Metaclass.
    Ensures one instance per class.
    """
    _instances = {}
    _lock: Lock = Lock()  # Class-level lock shared across all singletons

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                # Double-checked locking pattern
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Logger:
    """
    Logger that logs to console, file, and optionally to Elasticsearch with ECS format.
    """
    _logging_dict: Dict[str, int] = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    def __init__(
        self,
        log_file: str = "app.log",
        max_bytes: int = 10_000_000,
        backup_count: int = 5,
        es_url: Optional[str] = None,
        service_name: str = "default-service",
        log_level: str = "INFO"
    ) -> None:
        if hasattr(self, "_initialized"):
            return  # Prevent re-initialization

        self._initialized = True
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(self._logging_dict.get(log_level.upper(), logging.INFO))
        self.logger.propagate = False

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler with rotation
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Elasticsearch setup
        self.es_client: Optional[Elasticsearch] = None
        if es_url:
            try:
                self.es_client = Elasticsearch(es_url)
                self.logger.info("Connected to Elasticsearch at %s", es_url)
            except (ESConnectionError, ESTransportError) as e:
                self.logger.error("Failed to connect to Elasticsearch: %s", str(e))

    def _get_index_name(self) -> str:
        """
        Returns a daily ECS-compatible index name like logs-user-service-YYYY.MM.DD
        """
        today = datetime.now().strftime("%Y.%m.%d")
        return f"logs-{self.service_name}-{today}"

    def _transform_for_elasticsearch(self, level_name: str, message: str) -> Dict[str, str]:
        """
        Builds an ECS-compatible log document for Elasticsearch.
        """
        return {
            "@timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "message": message,
            "log.level": level_name.lower(),
            "service.name": self.service_name,
            "event.dataset": f"{self.service_name}.logs"
        }

    def log(self, level: int, message: str) -> None:
        """
        Logs to file, console, and Elasticsearch.
        """
        self.logger.log(level, message)

        if self.es_client:
            try:
                level_name = logging.getLevelName(level)
                log_entry = self._transform_for_elasticsearch(level_name, message)
                index_name = self._get_index_name()
                response = self.es_client.index(index=index_name, document=log_entry)
                self.logger.debug(f"ES index response: {response}")
            except ESTransportError as e:
                self.logger.error("Failed to log to Elasticsearch: %s", e)


    def debug(self, message: str) -> None:
        """Logs a message at DEBUG level."""
        self.log(logging.DEBUG, message)

    def info(self, message: str) -> None:
        """Logs a message at INFO level."""
        self.log(logging.INFO, message)

    def warning(self, message: str) -> None:
        """Logs a message at WARNING level."""
        self.log(logging.WARNING, message)

    def error(self, message: str) -> None:
        """Logs a message at ERROR level."""
        self.log(logging.ERROR, message)

    def critical(self, message: str) -> None:
        """Logs a message at CRITICAL level."""
        self.log(logging.CRITICAL, message)

if __name__ == "__main__":
    logger = Logger(
        es_url="http://localhost:9200",
        service_name="api-service",
        log_level="DEBUG"
    )

    logger.debug("Debugging application flow.")
    logger.info("Application started successfully.")
    logger.warning("Low disk space warning.")
    logger.error("Error while processing payment.")
    logger.critical("Critical system failure.")
