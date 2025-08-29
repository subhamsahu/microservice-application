"""Main module for the Server."""

# Standard library imports
from contextlib import asynccontextmanager
from os import getpid
from typing import AsyncGenerator, Union
import warnings

# Third-party imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

# Local imports
from app.core.config import config as app_config
from app.core.config import cors_settings
from app.core.constants import API_PREFIX, PROJECT_NAME, SERVICE_NAME, ELASTIC_SEARCH_INDEXES
from app.core.exceptions import DatabaseInitializeError, ServerStartError
from app.core.error_handler import register_all_errors
from app.core.database import init_db
from app.routers import app_router
from app.core.logger import logger
from app.services.rabbitmq.connection import rabbitmq_manager
from app.services.elasticsearch import elasticsearch_service
from app.core.middlewares import GatewayMiddleware

# Private imports
from server_shared.utils.formatters import display_dotted_string
from server_shared.utils.meta_classes import Singleton
from server_shared.middlewares.security_middleware import PreventHPPMiddleware, SecureHeadersMiddleware
from server_shared.middlewares.core_middlewares import BodySizeLimiterMiddleware

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="Duplicate Operation ID"
)  # Need to Fix this duplicate warning


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:  # pylint: disable=unused-argument
    '''Lifespan event for the FastAPI application.'''
    fastapi_server = Server()
    await fastapi_server.preprocessing()
    yield
    await fastapi_server.postprocessing()


class Server(metaclass=Singleton):
    """
    Represents a Server.

    Coordinates:
        - FastAPI application
        - Security middleware
        - Database connections
        - Error handling
        - Route management

    Attributes:
        - config (Config): Configuration settings.
        - app (FastAPI): FastAPI application instance.
        - logger (Logger): Logger instance.
        - elastic_service (ElasticSearchService): Elasticsearch service instance.
    """
    version = '0.0.1'

    def __init__(self):
        self.config = app_config
        self.service_name = SERVICE_NAME.capitalize()
        self.__app = FastAPI(
            title=PROJECT_NAME,
            description=f'A RESTful API service for {self.service_name} microservice.',
            version=Server.version,
            lifespan=lifespan,
        )
        self.logger = logger
        # Use singleton instances - no need to create new ones

    @property
    def elastic_service(self):
        """Get the singleton Elasticsearch service."""
        return elasticsearch_service
    
    @property
    def rabbitmq_manager(self):
        """Get the singleton RabbitMQ manager."""
        return rabbitmq_manager

    async def preprocessing(self):
        """Preprocessing tasks before the server starts."""
        self.logger.info(f"{self.service_name} is starting...")
        await self.initialize_database()
        await self.initialize_rabbitmq()
        self.logger.info("Preprocessing completed.")

    async def postprocessing(self):
        """Postprocessing tasks after the server stops."""
        from app.core.database import connection_obj
        self.logger.info(f"{self.service_name} is stopping...")
        
        # Close all singleton connections
        await connection_obj.disconnect()
        await self.elastic_service.close()
        await self.rabbitmq_manager.close()
        
        self.logger.info("All connections closed successfully.")
        self.logger.info("Postprocessing completed.")

    @property
    def app(self):
        """Returns the FastAPI application instance."""
        return self.__app

    def initialize_security_middleware(self):
        """Configures security middleware."""
        self.logger.info("Initializing security middleware...")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[self.config.API_GATEWAY_URL],
            allow_credentials=cors_settings.ALLOWED_CREDENTIALS,
            allow_methods=cors_settings.ALLOWED_METHODS,
            allow_headers=cors_settings.ALLOWED_HEADERS,
        )
        self.app.add_middleware(
            SessionMiddleware,
            secret_key=self.config.SECRET_KEY_ONE,
            max_age=24 * 7 * 3600,  # 1 week
        )
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]
        )

        self.app.add_middleware(PreventHPPMiddleware)
        self.app.add_middleware(SecureHeadersMiddleware)

    def initialize_application_middleware(self):
        """
        Configures application middleware.

        This method is a placeholder for adding any application level
        middleware in the future.
        """
        # Compression
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        self.app.add_middleware(BodySizeLimiterMiddleware,
                                max_body_size=200 * 1024 * 1024)
        self.app.add_middleware(GatewayMiddleware)

    def initialize_error_handlers(self):
        """Configures error handling."""
        register_all_errors(self.app)

    def initialize_routes(self):
        """Defines application routes."""
        self.app.include_router(router=app_router, prefix=API_PREFIX)
        # for route in self.app.routes:
        #     print(f"{route.name}: {route.path}")

    async def initialize_database(self):
        """Initialize the application database connection."""
        self.logger.info("Initializing database connection...")
        try:
            await init_db()  # Initialize the database schema
            self.logger.info("Database connection initialized successfully.")
        except Exception as error:
            self.logger.error(f"Database initialization failed: {error}")
            raise DatabaseInitializeError(
                "Failed to initialize database connection.") from error
        # Elasticsearch enablement
        if self.config.ENABLE_ES:
            self.logger.info("Checking Elasticsearch connection...")
            await self.elastic_service.initialize()
            await self.elastic_service.create_index(ELASTIC_SEARCH_INDEXES.CATALOG)
            self.logger.info("Elasticsearch connection is healthy.")

    async def initialize_rabbitmq(self):
        """Initialize RabbitMQ connection."""
        self.logger.info("Initializing RabbitMQ connection...")
        try:
            await self.rabbitmq_manager.initialize()
            self.logger.info("RabbitMQ connection initialized successfully.")
        except Exception as error:
            self.logger.error(f"RabbitMQ initialization failed: {error}")
            raise ServerStartError(
                "Failed to initialize RabbitMQ connection.") from error

    def initialize_server(self):
        """Initializes and starts the server."""
        self.initialize_security_middleware()
        self.initialize_application_middleware()
        self.initialize_error_handlers()
        self.initialize_routes()

    def start_server(self) -> Union[FastAPI, None]:
        """Starts the HTTP server."""
        try:
            self.initialize_server()
            self.logger.info(
                f"{self.service_name} has started with process id {getpid()}")
            display_dotted_string(f"{self.service_name}  started")
            return self.app
        except ServerStartError as error:
            self.logger.error(
                f"{self.service_name} start_server() error method: {error}")
            return None


server: Server = Server().start_server()  # type: ignore
