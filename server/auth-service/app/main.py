"""Main module for the Server."""

# Standard library imports
import logging
from contextlib import asynccontextmanager
from os import getpid
from typing import AsyncGenerator, Union
import warnings

# Third-party imports
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

# Local imports
from app.core.config import config as app_config
from app.core.config import cors_settings
from app.core.constants import API_PREFIX, PROJECT_NAME, SERVICE_NAME
from app.core.exceptions import AppException, DatabaseInitializeError, ServerStartError, register_all_errors
from app.core.database import init_db
from app.routers import app_router
from app.core.logger import logger
from app.services.rabbitmq.connection import create_rabbitmq_channel
from app.services.elasticsearch import ElasticSearchService
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
        self.elastic_service = ElasticSearchService(
            self.config.ELASTICSEARCH_URL)

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
        await connection_obj.disconnect()
        self.logger.info("Disconnected from DB")
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

        # Add global rate limiting middleware
        # init_rate_limiter(self.app)
        # self.app.middleware("http")(rate_limit_middleware())

    def initialize_error_handlers(self):
        """Configures error handling."""
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(_: Request, exc: RequestValidationError):
            return JSONResponse(
                status_code=422,
                content={"detail": exc.errors(), "body": exc.body},
            )

        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            # Handle 404 separately
            if exc.status_code == 404:
                full_url = str(request.url)
                self.logger.log(
                    logging.INFO, f"{full_url} endpoint does not exist.")
                return JSONResponse(
                    status_code=404,
                    content={"message": "The endpoint called does not exist."}
                )

            # General HTTPException handler
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail}
            )

        @self.app.exception_handler(AppException)
        async def unhandled_exception_handler(_: Request, exc: Exception):
            self.logger.log(logging.ERROR, f"Unhandled error: {str(exc)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
        register_all_errors(self.app)

    def initialize_routes(self):
        """Defines application routes."""
        self.app.include_router(router=app_router, prefix=API_PREFIX)
        for route in self.app.routes:
            print(f"{route.name}: {route.path}")

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
        # Uncomment if using Elasticsearch
        if self.config.ENABLE_ES:
            self.logger.info("Checking Elasticsearch connection...")
            self.elastic_service.check_connection()
            self.logger.info("Elasticsearch connection is healthy.")

    async def initialize_rabbitmq(self):
        """Initialize RabbitMQ connection."""
        self.logger.info("Initializing RabbitMQ connection...")
        try:
            await create_rabbitmq_channel()
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
