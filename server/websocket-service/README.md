# FastAPI Socket.IO WebSocket Service

A standalone FastAPI server with Socket.IO support for real-time WebSocket communication.

## Features

- **FastAPI Integration**: Full REST API capabilities with Socket.IO WebSocket support
- **Real-time Communication**: Bidirectional communication between client and server
- **Room Management**: Join/leave rooms for targeted messaging
- **Broadcasting**: Send messages to all connected clients
- **Built-in Test Client**: Web interface for testing WebSocket functionality
- **Health Monitoring**: Health check and client count endpoints

## Installation

1. Install dependencies using Poetry:
```bash
poetry install
```

2. Activate the virtual environment:
```bash
poetry shell
```

## Running the Server

### Development Mode
```bash
python server.py
```

### Production Mode
```bash
uvicorn server:socket_app --host 0.0.0.0 --port 8000
```

## Testing

Visit `http://localhost:8000` in your browser to access the built-in test client.

## API Endpoints

- `GET /` - Built-in WebSocket test client
- `GET /health` - Health check endpoint
- `GET /clients` - Get number of connected clients

## Socket.IO Events

### Client Events (sent from client to server)
- `message` - Send a message to the server
- `broadcast` - Broadcast a message to all connected clients
- `join_room` - Join a specific room
- `leave_room` - Leave a specific room
- `room_message` - Send a message to a specific room

### Server Events (sent from server to client)
- `message` - General messages from server
- `response` - Echo responses
- `broadcast` - Broadcasted messages
- `room_message` - Room-specific messages

## Usage Examples

### Basic Connection
```javascript
const socket = io('http://localhost:8000');

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('message', (data) => {
    console.log('Received:', data.msg);
});
```

### Sending Messages
```javascript
// Send a message
socket.emit('message', 'Hello Server!');

// Broadcast to all clients
socket.emit('broadcast', 'Hello Everyone!');

// Join a room
socket.emit('join_room', {room: 'chat-room-1'});

// Send message to room
socket.emit('room_message', {
    room: 'chat-room-1',
    message: 'Hello room!'
});
```

### Python Client Example
```python
import socketio

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print('Connected to server')

@sio.event
async def message(data):
    print('Received:', data['msg'])

async def main():
    await sio.connect('http://localhost:8000')
    await sio.emit('message', 'Hello from Python!')
    await sio.wait()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```

## Configuration

The server runs on `localhost:8000` by default. You can modify the configuration in `server.py`:

```python
uvicorn.run(
    "server:socket_app",
    host="0.0.0.0",  # Change host
    port=8000,       # Change port
    reload=True,     # Development mode
    log_level="info"
)
```

## Architecture

- **FastAPI**: Handles HTTP requests and serves the test client
- **Socket.IO**: Manages WebSocket connections and real-time events
- **ASGI**: Combines FastAPI and Socket.IO into a single application

## Error Handling

The server includes comprehensive error handling for:
- Connection failures
- Invalid room operations
- Message formatting errors
- Client disconnections