from fastapi import WebSocket
from typing import List, Dict

class ConnectionManager:
    def __init__(self):
        
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, username: str):
       
        await websocket.accept()
        
       
        if username not in self.active_connections:
            self.active_connections[username] = []
            
        
        self.active_connections[username].append(websocket)

    def disconnect(self, websocket: WebSocket, username: str):
        
        if username in self.active_connections:
            self.active_connections[username].remove(websocket)
            
            if len(self.active_connections[username]) == 0:
                del self.active_connections[username]

    async def send_personal_message(self, message: str, username: str):
        
        if username in self.active_connections:
            for connection in self.active_connections[username]:
                await connection.send_text(message)


manager = ConnectionManager()