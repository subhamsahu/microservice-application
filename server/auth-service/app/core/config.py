"""Configuration settings for the application."""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    """Base settings for the application."""
    DEVELOPMENT: bool = True

    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION_TIME: int  # in seconds
    JWT_REFRESH_EXPIRATION_TIME: int  # in seconds
    SECRET_KEY_ONE: str
    SECRET_KEY_TWO: str

    CLIENT_URL: str = Field(alias="CLIENT_URL")
    API_GATEWAY_URL: str = Field(alias="API_GATWAY_URL")
    SERVER_IP: str = "0.0.0.0"
    SERVER_PORT: int = 4002

    # Cloudinary Configuration
    CLOUDINARY_URL:str
    CLOUDINARY_CLOUD_NAME:str
    CLOUDINARY_API_KEY:str
    CLOUDINARY_API_SECRET:str

    # Database and Redis configuration
    DATABASE_URL: str = Field(alias="MYSQL_URL")
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = ""

    # RabbitMQ configuration
    RABBITMQ_ENDPOINT: str

    # Elasticsearch configuration
    ENABLE_ES: int = 0
    ELASTICSEARCH_URL: str = "http://localhost:9200"

    # APM configuration
    ENABLE_APM: int = 1
    ELASTIC_APM_SERVER_URL: str
    ELASTIC_APM_SECRET_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


# Bind environment variables to config object
config = ApplicationSettings()  # type: ignore


class CORSSettings(BaseSettings):
    """Application CORS settings."""
    ALLOWED_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])
    ALLOWED_METHODS: List[str] = Field(default_factory=lambda: ["*"])
    ALLOWED_HEADERS: List[str] = Field(default_factory=lambda: ["*"])
    ALLOWED_CREDENTIALS: bool = True


# add this line
config = ApplicationSettings()  # type: ignore
cors_settings = CORSSettings()  # type: ignore
