"""
This module contains constants used in the application.
"""
from dataclasses import dataclass

PROJECT_NAME = "Microservice Application"
SERVICE_NAME = "user-service"
API_PREFIX = "/api/v1"
DATABASE_NAME = f"{PROJECT_NAME.lower().replace(" ", "_")}_database"
# Allowed HTTP methods for CORS

# Database Collections
BUYER_COLLECTION = "buyers"
SELLER_COLLECTION = "sellers"

# Elasticsearch Indexes
@dataclass
class ELASTIC_SEARCH_INDEXES:
    """
    Elasticsearch index names used in the application.
    """
    BUYERS = "buyers"
    SELLERS = "sellers"

# Queue Names
BUYER_QUEUE = "user_buyer_queue"
SELLER_QUEUE = "user_seller_queue"
REVIEW_QUEUE = "review_queue"
SEED_GIG_QUEUE = "seed_gig_queue"
