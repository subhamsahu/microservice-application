"""
The router module for the FastAPI application
"""

from fastapi import APIRouter, status

from server_shared.utils.meta_classes import Singleton
from app.routers.health import router as health_router
from app.routers.chat import router as chat_router

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
            health_router, prefix="/chat", tags=["Health"])
        self.__router.include_router(
            chat_router, prefix="/chat", tags=["Chat"])

    @property
    def router(self):
        """
        Returns the main application router.
        """
        return self.__router

# Instantiate the BaseRouter
app_router = AppRouter().router