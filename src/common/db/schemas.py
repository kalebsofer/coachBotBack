from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

# ----- User Schemas -----
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    user_id: UUID

    class Config:
        from_attributes = True


# ----- Chat Schemas -----
class ChatBase(BaseModel):
    user_id: UUID

class ChatCreate(ChatBase):
    pass

class ChatRead(ChatBase):
    chat_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ----- Message Schemas -----
class MessageBase(BaseModel):
    chat_id: UUID
    sender_id: UUID = Field(..., alias="user_id")
    content: str
    user_message: bool = True

class MessageCreate(MessageBase):
    class Config:
        # In Pydantic v2, enable population by alias for input data.
        populate_by_alias = True

class MessageRead(MessageBase):
    message_id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


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
        from_attributes = True
