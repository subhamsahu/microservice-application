"""
This module contains constants used in the application.
"""
from dataclasses import dataclass

PROJECT_NAME = "Microservice Application"
SERVICE_NAME = "chat-service"
API_PREFIX = "/api/v1"
DATABASE_NAME = f"{PROJECT_NAME.lower().replace(" ", "_")}_database"
# Allowed HTTP methods for CORS

# Database Collections
CHAT_COLLECTION = "chat"
MESSAGE_COLLECTION = "messages"
ROOM_COLLECTION = "rooms"

# Elasticsearch Indexes
@dataclass
class ELASTIC_SEARCH_INDEXES:
    """
    Elasticsearch index names used in the application.
    """
    CHAT = "chat"
    MESSAGES = "messages"