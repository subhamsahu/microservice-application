"""Configuration settings for the application."""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    """Base settings for the application."""
    DEVELOPMENT: bool = True

    JWT_SECRET: str
    JWT_ALGORITHM: str
    SECRET_KEY_ONE: str
    SECRET_KEY_TWO: str
    CLIENT_URL: str = "http://example.com"
    SERVER_IP: str = "0.0.0.0"
    SERVER_PORT: int = 4001

    # Database and Redis configuration
    POSTGRES_DATABASE_URL: str
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379"

    # RabbitMQ configuration
    RABBITMQ_ENDPOINT: str = "amqp://labadmin:root123@localhost:5672"

    # Mail config
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    DOMAIN: str

    # Elasticsearch configuration
    ENABLE_ES_LOGGING: int = 0
    ELASTICSEARCH_URL: str = "http://elasticsearch.example.com"

    FIRST_SUPERUSER: str = "admin"
    FIRST_SUPERUSER_EMAIL: str =  "admin@domain.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin"

    TEST_USER: str = "user"
    TEST_USER_EMAIL: str = "user@domain.com"
    TEST_USER_PASSWORD: str = "user"

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
