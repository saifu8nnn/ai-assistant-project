from fastapi import WebSocket
from typing import List, Dict

class ConnectionManager:
    def __init__(self):
        # Yeh dictionary har user ke saare active devices track karegi
        # Format kaisa dikhega -> {"zaid": [websocket_pc, websocket_laptop]}
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, username: str):
        # Naya connection accept karo
        await websocket.accept()
        
        # Agar user pehli baar connect kar raha hai, toh uski list banao
        if username not in self.active_connections:
            self.active_connections[username] = []
            
        # Naye device ke connection ko list mein daal do
        self.active_connections[username].append(websocket)

    def disconnect(self, websocket: WebSocket, username: str):
        # Jab user tab band kare, toh connection hata do
        if username in self.active_connections:
            self.active_connections[username].remove(websocket)
            # Agar user ke saare tabs band ho gaye, toh uska naam dictionary se hata do
            if len(self.active_connections[username]) == 0:
                del self.active_connections[username]

    async def send_personal_message(self, message: str, username: str):
        # Main Logic: Ek user ke SAARE active devices par message push karo
        if username in self.active_connections:
            for connection in self.active_connections[username]:
                await connection.send_text(message)

# Iska ek global instance bana kar rakh lete hain
manager = ConnectionManager()