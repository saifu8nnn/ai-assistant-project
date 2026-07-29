from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# This is what the frontend MUST send us
class UserCreate(BaseModel):
    username: str
    password: str

# This is what we safely send back (notice there is no password here!)
class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

# This is the VIP Wristband format
class Token(BaseModel):
    access_token: str
    token_type: str
    
class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True