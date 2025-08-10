"""
The router module for the FastAPI application
"""

from fastapi import APIRouter, status

from server_shared.utils.meta_classes import Singleton
from app.routers.health import router as health_router
from app.routers.proxy import router as proxy_router
from app.core.constants import PROJECT_NAME, SERVICE_NAME

class AppRouter(metaclass=Singleton):
    """
    The main router for the FastAPI application
    """

    def __init__(self):
        self.__router: APIRouter = APIRouter()
        self.__register_routers()

    def __register_routers(self):
        """
        Registers routers with specific prefixes and tags to the main application router.
        """
        self.__router.include_router(
            health_router, prefix="/gateway-service", tags=["Health"])
        self.__router.include_router(
            proxy_router, prefix="/gateway", tags=["Proxy"])

    @property
    def router(self):
        """
        Returns the main application router.
        """
        return self.__router

    def app_welcome(self):
        """
        This is the welcome endpoint for the application.
        """
        return {
            "message": f"Welcome to the {PROJECT_NAME} {SERVICE_NAME}",
            "version": "1.0.0"
        }

# Instantiate the BaseRouter
app_router = AppRouter().router
