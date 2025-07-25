"""
Elasticsearch client configuration and connection check.
"""

# standard library imports
from time import sleep

# third-party imports
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as ESConnectionError

# private imports
from app.core.logger import logger
from app.core.config import config as app_config
from app.core.constants import SERVICE_NAME


class ElasticSearchService:
    """
    A class to manage Elasticsearch connection and health check.
    """

    def __init__(self, url: str = app_config.ELASTICSEARCH_URL):
        """
        Initializes the Elasticsearch client.
        :param url: URL of the Elasticsearch instance.
        """
        self.client = Elasticsearch(url)

    def check_connection(self) -> None:
        """
        Continuously checks the health of the Elasticsearch cluster until a successful connection is made.
        Logs the status after successful connection or error messages on failure.
        """
        is_connected = False
        while not is_connected:
            try:
                health = self.client.cluster.health()
                logger.info(f"{SERVICE_NAME.capitalize()} Elasticsearch health status - {health['status']}")
                is_connected = True
            except ESConnectionError as error:
                logger.error("Connection to Elasticsearch failed. Retrying...")
                logger.error(f"{SERVICE_NAME} check_connection() method: {error}")
                sleep(3)  # Backoff before retrying
