from fastapi import WebSocket
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        # Store active connections by user role
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "dispatcher": set(),
            "responder": set(),
            "supervisor": set(),
            "admin": set()
        }
        # Store user info for each connection
        self.connection_users: Dict[WebSocket, dict] = {}
    
    async def connect(self, websocket: WebSocket, user_role: str, user_id: int, username: str):
        await websocket.accept()
        
        # Add to appropriate role group
        if user_role in self.active_connections:
            self.active_connections[user_role].add(websocket)
        
        # Store user info
        self.connection_users[websocket] = {
            "user_id": user_id,
            "username": username,
            "role": user_role,
            "connected_at": datetime.utcnow()
        }
        
        # Send welcome message
        await self.send_personal_message(
            {
                "type": "connection_established",
                "message": f"Welcome {username}! Connected as {user_role}",
                "user": {
                    "id": user_id,
                    "username": username,
                    "role": user_role
                }
            },
            websocket
        )
    
    def disconnect(self, websocket: WebSocket):
        # Remove from role group
        user_info = self.connection_users.get(websocket)
        if user_info and user_info["role"] in self.active_connections:
            self.active_connections[user_info["role"]].discard(websocket)
        
        # Remove user info
        self.connection_users.pop(websocket, None)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast_to_role(self, message: dict, role: str):
        """Send message to all connections of a specific role"""
        if role in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[role]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    print(f"Error broadcasting to {role}: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.disconnect(connection)
    
    async def broadcast_to_all(self, message: dict):
        """Send message to all active connections"""
        disconnected = set()
        for role_connections in self.active_connections.values():
            for connection in role_connections:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    print(f"Error broadcasting to all: {e}")
                    disconnected.add(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_incident_update(self, incident_data: dict, roles: List[str] = None):
        """Send incident update to relevant roles"""
        message = {
            "type": "incident_update",
            "data": incident_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if roles:
            for role in roles:
                await self.broadcast_to_role(message, role)
        else:
            await self.broadcast_to_role(message, "dispatcher")
    
    async def send_unit_update(self, unit_data: dict, roles: List[str] = None):
        """Send unit update to relevant roles"""
        message = {
            "type": "unit_update",
            "data": unit_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if roles:
            for role in roles:
                await self.broadcast_to_role(message, role)
        else:
            await self.broadcast_to_role(message, "dispatcher")
    
    async def send_dispatch_update(self, dispatch_data: dict, roles: List[str] = None):
        """Send dispatch update to relevant roles"""
        message = {
            "type": "dispatch_update",
            "data": dispatch_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if roles:
            for role in roles:
                await self.broadcast_to_role(message, role)
        else:
            await self.broadcast_to_role(message, "dispatcher")
    
    def get_connection_count(self) -> Dict[str, int]:
        """Get count of active connections by role"""
        return {
            role: len(connections) 
            for role, connections in self.active_connections.items()
        }
    
    def get_user_info(self, websocket: WebSocket) -> dict:
        """Get user info for a specific connection"""
        return self.connection_users.get(websocket, {})

# Global manager instance
manager = ConnectionManager() 