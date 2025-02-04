from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

# ----- User Schemas -----
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    user_id: UUID

    class Config:
        orm_mode = True


# ----- Chat Schemas -----
class ChatBase(BaseModel):
    user_id: UUID

class ChatCreate(ChatBase):
    pass

class ChatRead(ChatBase):
    chat_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


# ----- Message Schemas -----
class MessageBase(BaseModel):
    chat_id: UUID
    sender_id: UUID
    content: str
    user_message: bool

class MessageCreate(MessageBase):
    pass

class MessageRead(MessageBase):
    message_id: UUID
    timestamp: datetime

    class Config:
        orm_mode = True


# ----- Log Schemas -----
class LogBase(BaseModel):
    user_id: UUID
    chat_id: UUID
    action: str
    details: Optional[str] = None

class LogCreate(LogBase):
    pass

class LogRead(LogBase):
    log_id: UUID
    timestamp: datetime

    class Config:
        orm_mode = True
