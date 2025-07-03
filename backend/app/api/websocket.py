from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from app.websocket.manager import manager
from app.core.auth import verify_token
from app.models.user import User
from app.core.database import SessionLocal
import json

router = APIRouter()

async def get_user_from_token(token: str) -> User:
    """Get user from JWT token"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    finally:
        db.close()

@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """WebSocket endpoint for real-time updates"""
    try:
        # Validate token and get user
        user = await get_user_from_token(token)
        
        # Connect to WebSocket
        await manager.connect(websocket, user.role.value, user.id, user.username)
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await manager.send_personal_message({"type": "pong"}, websocket)
                elif message.get("type") == "subscribe":
                    # Handle subscription to specific updates
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "channels": message.get("channels", [])
                    }, websocket)
                else:
                    # Echo back unknown messages
                    await manager.send_personal_message({
                        "type": "echo",
                        "data": message
                    }, websocket)
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                # Send error message to client
                await manager.send_personal_message({
                    "type": "error",
                    "message": str(e)
                }, websocket)
                
    except Exception as e:
        # Handle connection errors
        try:
            await websocket.close(code=1008, reason=str(e))
        except:
            pass
    finally:
        # Clean up connection
        manager.disconnect(websocket)

@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status"""
    return {
        "connections": manager.get_connection_count(),
        "total_connections": sum(manager.get_connection_count().values())
    } 