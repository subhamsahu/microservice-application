"""
The router module for the FastAPI application
"""

from fastapi import APIRouter, status

from server_shared.utils.meta_classes import Singleton
from app.routers.health import router as health_router
from app.routers.auth import router as auth_router

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
            health_router, prefix="/auth-service", tags=["Health"])
        self.__router.include_router(
            auth_router, prefix="/auth", tags=["Auth"])

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
            "message": "Welcome to the Microservice Application Notification Service",
            "version": "1.0.0"
        }


# Instantiate the BaseRouter
app_router = AppRouter().router
