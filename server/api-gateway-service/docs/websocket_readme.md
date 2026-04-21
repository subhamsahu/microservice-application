# 🔌 WebSocket Implementation in API Gateway Service

## 📋 Overview

This API Gateway service implements a **real-time WebSocket communication system** using Socket.IO that acts as a central hub, connecting frontend clients to multiple backend microservices. The implementation provides scalable, fault-tolerant real-time communication across your microservices architecture.

## 🏗️ Architecture

```
┌─────────────────┐    WebSocket     ┌──────────────────────┐    WebSocket     ┌─────────────────┐
│  Frontend       │ ◄─────────────► │   API Gateway        │ ◄─────────────► │  Chat Service   │
│  Client         │                 │   (Socket.IO Hub)    │                 │                 │
└─────────────────┘                 │                      │                 └─────────────────┘
                                    │  ┌─────────────────┐ │    WebSocket     ┌─────────────────┐
                                    │  │     Redis       │ │ ◄─────────────► │  Order Service  │
                                    │  │ (State & Scale) │ │                 │                 │
                                    │  └─────────────────┘ │                 └─────────────────┘
                                    └──────────────────────┘
```

## 🚀 Key Features

- **Unified Communication Hub**: Single WebSocket endpoint for all real-time communication
- **Microservice Integration**: Seamless connection to multiple backend services
- **Horizontal Scaling**: Redis-based clustering for multiple gateway instances
- **Fault Tolerance**: Continues operation even when downstream services are offline
- **CORS Support**: Configured for frontend integration
- **Real-time State Management**: Redis-backed user presence and state tracking

## 📁 File Structure

```
app/
├── main.py                    # Main server setup and Socket.IO initialization
├── sockets/
│   └── socket_handler.py      # WebSocket event handlers and service connections
├── services/
│   ├── gateway_service.py     # Redis-based state management
│   └── redis.py              # Redis connection management
└── core/
    └── config.py             # Configuration settings
```

## 🔧 Technical Implementation

### 1. Socket.IO Server Setup (`main.py`)

```python
def initialize_socketio(self):
    """Setup Socket.IO server with Redis as message broker."""
    # Redis manager for scaling across multiple server instances
    redis_url = self.config.REDIS_URL or f"redis://{self.config.REDIS_HOST.replace('redis://', '')}:6379"
    mgr = AsyncRedisManager(redis_url)

    # Create SocketIO server with Redis clustering support
    self.sio = AsyncServer(
        async_mode="asgi",                              # ASGI mode for FastAPI integration
        cors_allowed_origins=[self.config.CLIENT_URL], # CORS for frontend
        client_manager=mgr                              # Redis for horizontal scaling
    )

    # Register all event handlers
    socket_handler = SocketIOAppHandler(self.sio)
    socket_handler.listen()

    # Wrap FastAPI with Socket.IO - enables HTTP + WebSocket on same port
    self.asgi_app = ASGIApp(self.sio, other_asgi_app=self.__app)
```

**Key Points:**
- **ASGI Integration**: Same port (4000) handles both HTTP REST API and WebSocket connections
- **Redis Clustering**: Enables horizontal scaling across multiple gateway instances
- **CORS Configuration**: Allows frontend clients to connect securely

### 2. Event Handling (`socket_handler.py`)

#### Client-to-Gateway Events
```python
def _register_gateway_events(self):
    @self.sio.event
    async def connect(sid, environ):
        logger.info(f"[Gateway] Client connected: {sid}")

    @self.sio.on("getLoggedInUsers")
    async def get_logged_in_users(sid):
        users = await self.gateway_service.get_logged_in_users("loggedInUsers")
        await self.sio.emit("online", users)

    @self.sio.on("loggedInUsers")
    async def logged_in_users(sid, username: str):
        users = await self.gateway_service.save_logged_in_user("loggedInUsers", username)
        await self.sio.emit("online", users)
```

#### Service-to-Service Relay
```python
def _chat_service_io_connections(self):
    # Gateway connects to Chat Service as a client
    @self.chat_client.on("message received")
    async def message_received(data):
        # Relay messages from chat service to all frontend clients
        await self.sio.emit("message received", data)
```

### 3. State Management (`gateway_service.py`)

```python
async def save_logged_in_user(self, key: str, value: str) -> List[str]:
    """Save a logged-in user into Redis list if not already present."""
    if await self.client.lpos(key, value) is None:
        await self.client.lpush(key, value)
        logger.info(f"User {value} added")

    response = await self.client.lrange(key, 0, -1)
    return response
```

## 🎯 Supported Events

### Client → Gateway Events

| Event | Parameters | Description | Response |
|-------|------------|-------------|----------|
| `connect` | - | Client establishes connection | Session ID logged |
| `disconnect` | - | Client disconnects | Session cleanup |
| `getLoggedInUsers` | - | Request list of online users | `online` event with user list |
| `loggedInUsers` | `username: string` | Add user to online list | `online` event with updated list |
| `removeLoggedInUser` | `username: string` | Remove user from online list | `online` event with updated list |
| `category` | `category: string, username: string` | Save user's selected category | Stored in Redis |

### Gateway → Client Events

| Event | Data | Description |
|-------|------|-------------|
| `online` | `users: string[]` | Updated list of online users |
| `message received` | `data: object` | Real-time message from chat service |
| `message updated` | `data: object` | Message edit/update notification |
| `order notification` | `order: object, notification: object` | Order status updates |

## 🔄 Real-time Flow Examples

### User Login Flow
```javascript
// 1. Frontend connects and logs in user
const socket = io('http://localhost:4000');
socket.emit('loggedInUsers', 'john_doe');

// 2. Gateway processes login
// - Adds 'john_doe' to Redis list
// - Broadcasts updated user list to ALL clients

// 3. All clients receive updated user list
socket.on('online', (users) => {
    console.log('Online users:', users); // ['john_doe', 'alice', 'bob']
    updateUserListUI(users);
});
```

### Real-time Messaging
```javascript
// 1. Chat service emits message
// chatService.emit('message received', { text: 'Hello!', user: 'alice' });

// 2. Gateway relays to all frontend clients
socket.on('message received', (message) => {
    console.log('New message:', message);
    displayMessage(message);
});
```

## 🚦 Connection Management

### Server Startup Sequence
1. **FastAPI App Creation**: Standard FastAPI application setup
2. **Redis Connection**: Establish connection to Redis server
3. **Socket.IO Initialization**: Create Socket.IO server with Redis manager
4. **Event Handler Registration**: Register all WebSocket event handlers
5. **Downstream Service Connection**: Connect to chat and order services (with error handling)
6. **ASGI Wrapper**: Wrap FastAPI app with Socket.IO using `ASGIApp`
7. **Server Start**: Launch unified HTTP + WebSocket server on port 4000

### Error Handling
```python
# Graceful handling of downstream service failures
async def connect_downstream_services(self):
    try:
        await self.chat_client.connect(config.MESSAGE_BASE_URL)
        logger.info("Successfully connected to chat service")
    except Exception as e:
        logger.warning(f"Failed to connect to chat service: {e}")
        # Server continues running even if downstream services are down
```

## 📊 Data Storage

### Redis Data Structures

| Key Pattern | Type | Purpose | Example |
|-------------|------|---------|---------|
| `loggedInUsers` | List | Track online users | `['alice', 'bob', 'charlie']` |
| `selectedCategories:{username}` | String | User preferences | `selectedCategories:alice` → `"electronics"` |

### Redis Operations
- **User Management**: `LPUSH`, `LRANGE`, `LREM`, `LPOS` for user lists
- **Preferences**: `SET`, `GET` for user settings
- **Pub/Sub**: Automatic via `AsyncRedisManager` for multi-instance scaling

## 🔧 Configuration

### Environment Variables (`.env`)
```bash
# Server Configuration
SERVER_IP=0.0.0.0
SERVER_PORT=4000
CLIENT_URL=http://localhost:3000

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379

# Service URLs
MESSAGE_BASE_URL=http://localhost:4005
ORDER_BASE_URL=http://localhost:4006
```

### CORS Configuration
```python
cors_allowed_origins=[self.config.CLIENT_URL]  # Frontend origin
```

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- Redis server running on localhost:6379
- Virtual environment activated

### Installation
```bash
# Install dependencies
pip install python-socketio fastapi uvicorn redis

# Or use the project's virtual environment
.venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Server
```bash
# Navigate to the API Gateway directory
cd server/api-gateway-service

# Run the server
python server.py
```

The server will start on `http://localhost:4000` with WebSocket support at `ws://localhost:4000/socket.io/`.

### Testing WebSocket Connection

#### JavaScript (Browser)
```javascript
const socket = io('http://localhost:4000');

socket.on('connect', () => {
    console.log('Connected to API Gateway');
    
    // Test user login
    socket.emit('loggedInUsers', 'test_user');
});

socket.on('online', (users) => {
    console.log('Online users:', users);
});
```

#### Python Client
```python
import socketio

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print('Connected to API Gateway')
    await sio.emit('loggedInUsers', 'test_user')

@sio.on('online')
async def on_online(users):
    print(f'Online users: {users}')

await sio.connect('http://localhost:4000')
```

## 🔍 Monitoring & Debugging

### Logs
The application provides detailed logging for:
- Client connections/disconnections
- Event processing
- Redis operations
- Downstream service connections
- Error handling

### Log Examples
```
2025-09-29 20:58:09,631 - INFO - [api-gateway-service] Api-gateway-service is starting...
2025-09-29 20:58:09,633 - INFO - [api-gateway-service] Connected to Redis at redis://localhost:6379
2025-09-29 20:58:09,635 - INFO - [api-gateway-service] Attempting to connect to chat service...
2025-09-29 20:58:11,918 - WARNING - [api-gateway-service] Failed to connect to chat service: Connection refused
2025-09-29 20:58:14,204 - INFO - [api-gateway-service] Preprocessing completed.
INFO:     Application startup complete.
```

## 🔮 Scaling Considerations

### Horizontal Scaling
- **Multiple Gateway Instances**: Run multiple API Gateway servers
- **Load Balancer**: Use nginx or similar to distribute WebSocket connections
- **Redis Clustering**: Redis handles pub/sub across all instances
- **Session Affinity**: Not required due to Redis state sharing

### Performance Optimization
- **Connection Pooling**: Redis connection pooling for high throughput
- **Event Batching**: Batch multiple events for efficiency
- **Room Management**: Use Socket.IO rooms for targeted broadcasts

## 🛠️ Troubleshooting

### Common Issues

1. **Server Won't Start**
   - Check if Redis is running: `redis-cli ping`
   - Verify port 4000 is available
   - Check environment variables in `.env`

2. **WebSocket Connection Failed**
   - Verify CORS settings match frontend URL
   - Check firewall settings for port 4000
   - Ensure client is using correct URL format

3. **Downstream Services Not Connecting**
   - Services will log warnings but continue running
   - Check service URLs in configuration
   - Verify downstream services are running

### Debug Mode
```python
# Enable detailed Socket.IO logging
import logging
logging.getLogger('socketio').setLevel(logging.DEBUG)
logging.getLogger('engineio').setLevel(logging.DEBUG)
```

## 📚 Dependencies

### Core Dependencies
- **python-socketio**: WebSocket implementation
- **fastapi**: Web framework and ASGI support
- **redis**: Redis client for state management
- **uvicorn**: ASGI server

### Development Dependencies
- **pytest**: Testing framework
- **typer**: CLI tools

## 🤝 Contributing

When adding new WebSocket events:

1. **Add Event Handler**: In `socket_handler.py`
2. **Update Documentation**: Add to this README
3. **Add Tests**: Create test cases for new events
4. **Update Frontend**: Corresponding client-side handlers

## 📄 License

This project is part of the microservice-application and follows the same licensing terms.

---

**🎉 Your API Gateway WebSocket service is now ready for real-time communication across your microservices ecosystem!**