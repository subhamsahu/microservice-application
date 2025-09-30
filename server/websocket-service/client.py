"""
Advanced FastAPI Socket.IO client example
"""

import asyncio
import socketio
import json
from typing import Dict, Any

class WebSocketClient:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.sio = socketio.AsyncClient()
        self.server_url = server_url
        self.connected = False
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        """Set up event handlers for Socket.IO events"""
        
        @self.sio.event
        async def connect():
            self.connected = True
            print(f"✅ Connected to server at {self.server_url}")
        
        @self.sio.event
        async def disconnect():
            self.connected = False
            print("❌ Disconnected from server")
        
        @self.sio.event
        async def connect_error(data):
            print(f"❌ Connection error: {data}")
        
        @self.sio.event
        async def message(data):
            print(f"📨 Received message: {data['msg']}")
        
        @self.sio.event
        async def response(data):
            print(f"↩️ Response: {data['msg']}")
        
        @self.sio.event
        async def broadcast(data):
            print(f"📢 Broadcast from {data['from']}: {data['msg']}")
        
        @self.sio.event
        async def room_message(data):
            print(f"🏠 Room message from {data['from']}: {data['msg']}")
    
    async def connect_to_server(self):
        """Connect to the Socket.IO server"""
        try:
            await self.sio.connect(self.server_url)
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    async def disconnect_from_server(self):
        """Disconnect from the server"""
        if self.connected:
            await self.sio.disconnect()
    
    async def send_message(self, message: str):
        """Send a message to the server"""
        if self.connected:
            await self.sio.emit('message', message)
        else:
            print("Not connected to server")
    
    async def broadcast_message(self, message: str):
        """Broadcast a message to all connected clients"""
        if self.connected:
            await self.sio.emit('broadcast', message)
        else:
            print("Not connected to server")
    
    async def join_room(self, room_name: str):
        """Join a specific room"""
        if self.connected:
            await self.sio.emit('join_room', {'room': room_name})
            print(f"🚪 Joining room: {room_name}")
        else:
            print("Not connected to server")
    
    async def leave_room(self, room_name: str):
        """Leave a specific room"""
        if self.connected:
            await self.sio.emit('leave_room', {'room': room_name})
            print(f"🚪 Leaving room: {room_name}")
        else:
            print("Not connected to server")
    
    async def send_room_message(self, room_name: str, message: str):
        """Send a message to a specific room"""
        if self.connected:
            await self.sio.emit('room_message', {
                'room': room_name,
                'message': message
            })
        else:
            print("Not connected to server")
    
    async def wait_for_events(self):
        """Wait for events (keeps the client running)"""
        await self.sio.wait()


async def interactive_client():
    """Interactive client for testing the WebSocket server"""
    client = WebSocketClient()
    
    if not await client.connect_to_server():
        return
    
    print("\n🎮 Interactive WebSocket Client")
    print("Commands:")
    print("  msg <message>     - Send a message")
    print("  broadcast <msg>   - Broadcast to all clients")
    print("  join <room>       - Join a room")
    print("  leave <room>      - Leave a room")
    print("  room <room> <msg> - Send message to room")
    print("  quit              - Exit")
    print()
    
    try:
        while True:
            command = input("🔤 Enter command: ").strip()
            
            if command.lower() == 'quit':
                break
            
            parts = command.split(' ', 2)
            cmd = parts[0].lower()
            
            if cmd == 'msg' and len(parts) > 1:
                await client.send_message(' '.join(parts[1:]))
            
            elif cmd == 'broadcast' and len(parts) > 1:
                await client.broadcast_message(' '.join(parts[1:]))
            
            elif cmd == 'join' and len(parts) > 1:
                await client.join_room(parts[1])
            
            elif cmd == 'leave' and len(parts) > 1:
                await client.leave_room(parts[1])
            
            elif cmd == 'room' and len(parts) > 2:
                await client.send_room_message(parts[1], parts[2])
            
            else:
                print("❌ Invalid command")
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    
    finally:
        await client.disconnect_from_server()
        print("👋 Goodbye!")


async def automated_demo():
    """Automated demo of WebSocket functionality"""
    print("🤖 Starting automated demo...")
    
    # Create multiple clients
    client1 = WebSocketClient()
    client2 = WebSocketClient()
    
    # Connect both clients
    await client1.connect_to_server()
    await asyncio.sleep(1)
    await client2.connect_to_server()
    await asyncio.sleep(1)
    
    # Demo basic messaging
    print("\n📨 Testing basic messaging...")
    await client1.send_message("Hello from client 1!")
    await asyncio.sleep(1)
    await client2.send_message("Hello from client 2!")
    await asyncio.sleep(2)
    
    # Demo broadcasting
    print("\n📢 Testing broadcasting...")
    await client1.broadcast_message("This is a broadcast from client 1!")
    await asyncio.sleep(2)
    
    # Demo room functionality
    print("\n🏠 Testing room functionality...")
    await client1.join_room("demo-room")
    await asyncio.sleep(1)
    await client2.join_room("demo-room")
    await asyncio.sleep(1)
    
    await client1.send_room_message("demo-room", "Room message from client 1!")
    await asyncio.sleep(1)
    await client2.send_room_message("demo-room", "Room message from client 2!")
    await asyncio.sleep(2)
    
    # Clean up
    await client1.leave_room("demo-room")
    await client2.leave_room("demo-room")
    await asyncio.sleep(1)
    
    await client1.disconnect_from_server()
    await client2.disconnect_from_server()
    
    print("✅ Demo completed!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        asyncio.run(automated_demo())
    else:
        asyncio.run(interactive_client())