"""
This module contains constants used in the application.
"""
from dataclasses import dataclass

PROJECT_NAME = "Microservice Application"
SERVICE_NAME = "auth-service"
API_PREFIX = "/api/v1"
DATABASE_NAME = f"{PROJECT_NAME.lower().replace(" ", "_")}_database"
# Allowed HTTP methods for CORS

@dataclass
class ELASTIC_SEARCH_INDEXES:
    CATALOG = "catalog"
