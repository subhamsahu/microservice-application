"""
This module contains the main entry point for the application
"""

from fastapi import FastAPI

from app.main import Server
from app.core.config import config as app_config


class Application:
    """Application Class for Server
    """

    def initialize(self) -> FastAPI:
        """
        Initializes a FastAPI application instance.

        Initializes a FastAPI application instance and hands over control to the server.
        object to manage the application services.

        Returns the initialized FastAPI application instance.
        """
        server: Server = Server()
        fastapi_app: FastAPI = server.start_server()  # type: ignore
        return fastapi_app


# Instantiate and run the application
application: Application = Application()
app: FastAPI = application.initialize()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:server",  # Replace with the actual module path
                host=app_config.SERVER_IP,
                port=app_config.SERVER_PORT,
                reload=True,
                proxy_headers=True  # Enables trust in X-Forwarded-* headers
            )

# https://www.youtube.com/watch?v=KL6CjNxkZDQ
# https://www.youtube.com/watch?v=HTSK6eRwyGM
