from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base User schema."""

    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a User."""


class UserRead(UserBase):
    """Schema for reading a User."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configure Pydantic to handle SQLAlchemy models."""

        from_attributes = True


class ChatBase(BaseModel):
    """Base Chat schema."""

    user_id: UUID


class ChatCreate(ChatBase):
    """Schema for creating a Chat."""


class ChatRead(ChatBase):
    """Schema for reading a Chat."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    """Base Message schema."""

    chat_id: UUID
    sender_id: UUID
    content: str


class MessageCreate(MessageBase):
    """Schema for creating a Message."""


class MessageRead(MessageBase):
    """Schema for reading a Message."""

    id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


class LogBase(BaseModel):
    """Base Log schema."""

    user_id: UUID
    chat_id: UUID
    action: str
    details: Optional[str] = None


class LogCreate(LogBase):
    """Schema for creating a Log."""


class LogRead(LogBase):
    """Schema for reading a Log."""

    id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True
