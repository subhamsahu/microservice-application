from socketio import AsyncServer
from server_shared.utils.meta_classes import Singleton
class SocketServer(metaclass=Singleton):
    def __init__(self):
        self.__sio = AsyncServer(
            async_mode='asgi',
            cors_allowed_origins=["*"],  # Changed from string to list
            cors_credentials=True,
            logger=True,
            engineio_logger=True,
            ping_timeout=60,
            ping_interval=25
        )
    @property
    def sio(self):
        return self.__sio

sio = SocketServer().sio