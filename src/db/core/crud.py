from typing import Any, Generic, Optional, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Base, Chat, Log, Message, User
from .schemas import (
    ChatCreate,
    ChatRead,
    LogCreate,
    LogRead,
    MessageCreate,
    MessageRead,
    UserCreate,
    UserRead,
)

# Generic type for SQLAlchemy models
ModelType = TypeVar("ModelType", bound=Base)
# Generic types for Pydantic schemas
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, ReadSchemaType]):
    """Base class for CRUD operations."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(
        self, db: AsyncSession, *, obj_in: CreateSchemaType
    ) -> ReadSchemaType:
        """Create a new record."""
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        """Get a record by ID."""
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Get multiple records with pagination."""
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: dict[str, Any]
    ) -> ModelType:
        """Update a record."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: UUID) -> Optional[ModelType]:
        """Delete a record."""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj


class CRUDUser(CRUDBase[User, UserCreate, UserRead]):
    """CRUD operations for User model."""

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Get a user by email."""
        query = select(self.model).where(self.model.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()


class CRUDChat(CRUDBase[Chat, ChatCreate, ChatRead]):
    """CRUD operations for Chat model."""

    async def get_user_chats(self, db: AsyncSession, *, user_id: UUID) -> list[Chat]:
        """Get all chats for a user."""
        query = select(self.model).where(self.model.user_id == user_id)
        result = await db.execute(query)
        return list(result.scalars().all())


class CRUDMessage(CRUDBase[Message, MessageCreate, MessageRead]):
    """CRUD operations for Message model."""

    async def get_chat_messages(
        self, db: AsyncSession, *, chat_id: UUID
    ) -> list[Message]:
        """Get all messages in a chat."""
        query = (
            select(self.model)
            .where(self.model.chat_id == chat_id)
            .order_by(self.model.timestamp)
        )
        result = await db.execute(query)
        return list(result.scalars().all())


class CRUDLog(CRUDBase[Log, LogCreate, LogRead]):
    """CRUD operations for Log model."""

    async def get_chat_logs(self, db: AsyncSession, *, chat_id: UUID) -> list[Log]:
        """Get all logs for a chat."""
        query = (
            select(self.model)
            .where(self.model.chat_id == chat_id)
            .order_by(self.model.timestamp)
        )
        result = await db.execute(query)
        return list(result.scalars().all())


user = CRUDUser(User)
chat = CRUDChat(Chat)
message = CRUDMessage(Message)
log = CRUDLog(Log)
