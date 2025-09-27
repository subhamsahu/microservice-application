"""
This module contains constants used in the application.
"""
from dataclasses import dataclass

PROJECT_NAME = "Microservice Application"
SERVICE_NAME = "catalog-service"
API_PREFIX = "/api/v1"
DATABASE_NAME = f"{PROJECT_NAME.lower().replace(" ", "_")}_database"
# Allowed HTTP methods for CORS

# Database Collections
CATALOG_COLLECTION = "catalog"

# Elasticsearch Indexes
@dataclass
class ELASTIC_SEARCH_INDEXES:
    """
    Elasticsearch index names used in the application.
    """
    CATALOG = "catalog"

