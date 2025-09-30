from socketio import AsyncClient
from socketio import AsyncServer
from app.core.config import config
from app.core.logger import logger

class SocketHandler:
    """Handles WebSocket events using Socket.IO."""
    def __init__(self, sio: AsyncServer):
        self.sio = sio

    def register_events(self):
        self.__register_gateway_events()

    def __register_gateway_events(self):
        @self.sio.event
        async def connect(sid, environ, auth):
            try:
                logger.info(f"Client attempting to connect: {sid}")
                # logger.info(f"[Gateway] Connection environ keys: {list(environ.keys())}")
                # logger.info(f"[Gateway] HTTP_ORIGIN: {environ.get('HTTP_ORIGIN', 'Not set')}")
                # logger.info(f"[Gateway] QUERY_STRING: {environ.get('QUERY_STRING', 'Not set')}")
                # logger.info(f"[Gateway] REQUEST_METHOD: {environ.get('REQUEST_METHOD', 'Not set')}")
                # logger.info(f"[Gateway] PATH_INFO: {environ.get('PATH_INFO', 'Not set')}")
                # logger.info(f"[Gateway] User-Agent: {environ.get('HTTP_USER_AGENT', 'Not set')}")
                # logger.info(f"[Gateway] Auth data: {auth}")
                
                # Accept the connection
                logger.info(f"Client connected successfully: {sid}")
                # Send welcome message like the working websocket service
                await self.sio.emit('message', {'msg': f'Welcome to Chat Service! Your session ID is {sid}'}, room=sid)
                return True
                
            except Exception as e:
                logger.error(f"Connection error for {sid}: {e}")
                return False  # Reject connection
            
        @self.sio.event
        async def connect_error(sid, data):
            logger.error(f"[Gateway] Connection error for {sid}: {data}")

        @self.sio.event
        async def disconnect(sid):
            logger.info(f"[Gateway] Client disconnected: {sid}")

        
        # Add basic message handler for testing (like in working websocket service)
        @self.sio.event
        async def message(sid, data):
            """Handle incoming messages - for testing"""
            logger.info(f"[Gateway] Message from {sid}: {data}")
            # Echo the message back to the client
            await self.sio.emit('response', {'msg': f'Echo from Gateway: {data}'}, room=sid)

        # Add broadcast handler for testing
        @self.sio.event
        async def broadcast(sid, data):
            """Broadcast message to all connected clients"""
            logger.info(f"[Gateway] Broadcasting from {sid}: {data}")
            await self.sio.emit('broadcast', {'msg': data, 'from': sid})