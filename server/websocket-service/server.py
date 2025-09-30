"""
FastAPI Server with Socket.IO WebSocket Support
"""

import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import socketio

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# Create FastAPI app
app = FastAPI(
    title="FastAPI Socket.IO Server",
    description="A FastAPI server with Socket.IO WebSocket support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO event handlers
@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    print(f"Client {sid} connected")
    await sio.emit('message', {'msg': f'Welcome! Your session ID is {sid}'}, room=sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    print(f"Client {sid} disconnected")

@sio.event
async def message(sid, data):
    """Handle incoming messages"""
    print(f"Message from {sid}: {data}")
    # Echo the message back to the client
    await sio.emit('response', {'msg': f'Echo: {data}'}, room=sid)

@sio.event
async def broadcast(sid, data):
    """Broadcast message to all connected clients"""
    print(f"Broadcasting from {sid}: {data}")
    await sio.emit('broadcast', {'msg': data, 'from': sid})

@sio.event
async def join_room(sid, data):
    """Join a specific room"""
    room = data.get('room')
    if room:
        await sio.enter_room(sid, room)
        await sio.emit('message', {'msg': f'Joined room: {room}'}, room=sid)
        await sio.emit('room_message', {'msg': f'User {sid} joined the room'}, room=room)

@sio.event
async def leave_room(sid, data):
    """Leave a specific room"""
    room = data.get('room')
    if room:
        await sio.leave_room(sid, room)
        await sio.emit('message', {'msg': f'Left room: {room}'}, room=sid)
        await sio.emit('room_message', {'msg': f'User {sid} left the room'}, room=room)

@sio.event
async def room_message(sid, data):
    """Send message to a specific room"""
    room = data.get('room')
    message = data.get('message')
    if room and message:
        await sio.emit('room_message', {'msg': message, 'from': sid}, room=room)

# FastAPI routes
@app.get("/")
async def get_home():
    """Serve a simple test page"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI Socket.IO Test</title>
        <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .messages { height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; margin: 10px 0; }
            input, button { margin: 5px; padding: 10px; }
            input[type="text"] { width: 300px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>FastAPI Socket.IO Test Client</h1>
            <div id="status">Disconnected</div>
            
            <div class="messages" id="messages"></div>
            
            <div>
                <input type="text" id="messageInput" placeholder="Enter message...">
                <button onclick="sendMessage()">Send Message</button>
                <button onclick="broadcast()">Broadcast</button>
            </div>
            
            <div>
                <input type="text" id="roomInput" placeholder="Room name...">
                <button onclick="joinRoom()">Join Room</button>
                <button onclick="leaveRoom()">Leave Room</button>
            </div>
            
            <div>
                <input type="text" id="roomMessageInput" placeholder="Room message...">
                <button onclick="sendRoomMessage()">Send to Room</button>
            </div>
        </div>

        <script>
            const socket = io();
            
            socket.on('connect', function() {
                document.getElementById('status').textContent = 'Connected';
                addMessage('Connected to server');
            });
            
            socket.on('disconnect', function() {
                document.getElementById('status').textContent = 'Disconnected';
                addMessage('Disconnected from server');
            });
            
            socket.on('message', function(data) {
                addMessage('Server: ' + data.msg);
            });
            
            socket.on('response', function(data) {
                addMessage('Response: ' + data.msg);
            });
            
            socket.on('broadcast', function(data) {
                addMessage('Broadcast from ' + data.from + ': ' + data.msg);
            });
            
            socket.on('room_message', function(data) {
                addMessage('Room message from ' + data.from + ': ' + data.msg);
            });
            
            function addMessage(message) {
                const messages = document.getElementById('messages');
                const messageElement = document.createElement('div');
                messageElement.textContent = new Date().toLocaleTimeString() + ' - ' + message;
                messages.appendChild(messageElement);
                messages.scrollTop = messages.scrollHeight;
            }
            
            function sendMessage() {
                const input = document.getElementById('messageInput');
                if (input.value) {
                    socket.emit('message', input.value);
                    input.value = '';
                }
            }
            
            function broadcast() {
                const input = document.getElementById('messageInput');
                if (input.value) {
                    socket.emit('broadcast', input.value);
                    input.value = '';
                }
            }
            
            function joinRoom() {
                const input = document.getElementById('roomInput');
                if (input.value) {
                    socket.emit('join_room', {room: input.value});
                }
            }
            
            function leaveRoom() {
                const input = document.getElementById('roomInput');
                if (input.value) {
                    socket.emit('leave_room', {room: input.value});
                }
            }
            
            function sendRoomMessage() {
                const roomInput = document.getElementById('roomInput');
                const messageInput = document.getElementById('roomMessageInput');
                if (roomInput.value && messageInput.value) {
                    socket.emit('room_message', {
                        room: roomInput.value,
                        message: messageInput.value
                    });
                    messageInput.value = '';
                }
            }
            
            // Allow Enter key to send messages
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            document.getElementById('roomMessageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendRoomMessage();
                }
            });
        </script>
    </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "FastAPI Socket.IO server is running"}

@app.get("/clients")
async def get_connected_clients():
    """Get number of connected clients"""
    clients = len(sio.manager.rooms.get('/', {}))
    return {"connected_clients": clients}

# Create ASGI application
socket_app = socketio.ASGIApp(sio, app)

if __name__ == "__main__":
    print("Starting FastAPI server with Socket.IO support...")
    print("Visit http://localhost:8000 to test the WebSocket connection")
    uvicorn.run(
        "server:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )