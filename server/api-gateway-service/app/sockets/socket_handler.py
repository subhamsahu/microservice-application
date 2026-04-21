from socketio import AsyncClient
from socketio import AsyncServer
from app.core.config import config
from app.core.logger import logger
from app.services.gateway_service import GatewayService

class SocketHandler:
    """Handles WebSocket events using Socket.IO."""
    def __init__(self, sio: AsyncServer):
        self.sio = sio
        self.gateway_service = GatewayService()
        # Clients to other services
        self.chat_client = AsyncClient()
        self.order_client = AsyncClient()

    def register_events(self):
        self.__register_gateway_events()
        self._chat_service_io_connections()

    def __register_gateway_events(self):
        @self.sio.event
        async def connect(sid, environ, auth):
            try:
                logger.info(f"[Gateway] Client attempting to connect: {sid}")
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
                await self.sio.emit('message', {'msg': f'Welcome to API Gateway! Your session ID is {sid}'}, room=sid)
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

        @self.sio.on("getLoggedInUsers")
        async def get_logged_in_users(sid):
            users = await self.gateway_service.get_logged_in_users("loggedInUsers")
            await self.sio.emit("online", users)

        @self.sio.on("loggedInUsers")
        async def logged_in_users(sid, username: str):
            users = await self.gateway_service.save_logged_in_user("loggedInUsers", username)
            await self.sio.emit("online", users)

        @self.sio.on("removeLoggedInUser")
        async def remove_logged_in_user(sid, username: str):
            users = await self.gateway_service.remove_logged_in_user("loggedInUsers", username)
            await self.sio.emit("online", users)

        @self.sio.on("category")
        async def category(sid, category: str, username: str):
            await self.gateway_service.save_user_selected_category(f"selectedCategories:{username}", category)
        # -----------------------
    # Chat Service Connection
    # -----------------------
    def _chat_service_io_connections(self):
        @self.chat_client.event
        async def connect():
            logger.info("ChatService socket connected")

        @self.chat_client.event
        async def disconnect():
            logger.error("ChatService socket disconnected, reconnecting...")
            await self.chat_client.connect(config.MESSAGE_BASE_URL)

        @self.chat_client.event
        async def connect_error(data):
            logger.error(f"ChatService connection error: {data}")
            await self.chat_client.connect(config.MESSAGE_BASE_URL)

        # Relay events
        @self.chat_client.on("message received")
        async def message_received(data):
            logger.info(f"Relaying message received: {data}")
            await self.sio.emit("message received", data)

        @self.chat_client.on("message updated")
        async def message_updated(data):
            logger.info(f"Relaying message updated: {data}")
            await self.sio.emit("message updated", data)

    # -----------------------
    # Order Service Connection
    # -----------------------
    def _order_service_io_connections(self):
        @self.order_client.event
        async def connect():
            logger.info("OrderService socket connected")

        @self.order_client.event
        async def disconnect():
            logger.error("OrderService socket disconnected, reconnecting...")
            await self.order_client.connect(config.ORDER_BASE_URL)

        @self.order_client.event
        async def connect_error(data):
            logger.error(f"OrderService connection error: {data}")
            await self.order_client.connect(config.ORDER_BASE_URL)

        # Relay event
        @self.order_client.on("order notification")
        async def order_notification(order, notification):
            await self.sio.emit("order notification", order, notification)

    # -----------------------
    # Connect both clients
    # -----------------------
    async def connect_downstream_services(self):
        """Connect to downstream services with error handling"""
        try:
            logger.info("Attempting to connect to chat service...")
            await self.chat_client.connect(config.MESSAGE_BASE_URL, retry=False)
            logger.info("Successfully connected to chat service")
        except Exception as e:
            logger.warning(f"Failed to connect to chat service at {config.MESSAGE_BASE_URL}: {e}")
            
        try:
            logger.info("Attempting to connect to order service...")
            await self.order_client.connect(config.ORDER_BASE_URL, retry=False)
            logger.info("Successfully connected to order service")
        except Exception as e:
            logger.warning(f"Failed to connect to order service at {config.ORDER_BASE_URL}: {e}")
