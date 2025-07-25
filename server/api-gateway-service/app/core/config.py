"""Configuration settings for the application."""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class ApplicationSettings(BaseSettings):
    """Base settings for the application."""

    # General settings
    DEVELOPMENT: bool = True

    # JWT settings
    JWT_TOKEN: str
    GATEWAY_JWT_TOKEN: str
    SECRET_KEY_ONE: str
    SECRET_KEY_TWO: str

    # Server and client URLs
    SERVER_IP: str = "0.0.0.0"
    SERVER_PORT: int = 4000
    CLIENT_URL: str = "http://localhost:3000"

    # Redis settings
    REDIS_HOST: str = "redis://localhost:6379"
    REDIS_PORT: int = 6379
    REDIS_URL: str = ""

    # Service base URLs
    AUTH_BASE_URL: str
    USERS_BASE_URL: str
    CATALOG_BASE_URL: str
    MESSAGE_BASE_URL: str
    ORDER_BASE_URL: str
    REVIEW_BASE_URL: str

    # Elasticsearch settings
    ENABLE_ES: int = 0
    ELASTICSEARCH_URL: str = "http://localhost:9200"

    # APM settings
    ENABLE_APM: int = 0
    ELASTIC_APM_SERVER_URL: str
    ELASTIC_APM_SECRET_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


class CORSSettings(BaseSettings):
    """Application CORS settings."""
    ALLOWED_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])
    ALLOWED_METHODS: List[str] = Field(default_factory=lambda: ["*"])
    ALLOWED_HEADERS: List[str] = Field(default_factory=lambda: ["*"])
    ALLOWED_CREDENTIALS: bool = True


# add this line
config = ApplicationSettings()  # type: ignore
cors_settings = CORSSettings()  # type: ignore
