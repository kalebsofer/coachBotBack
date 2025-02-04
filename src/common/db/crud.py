from typing import Any, Generic, Optional, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.models import Base, Chat, Log, Message, User
from common.db.schemas import (
    ChatCreate,
    ChatRead,
    LogCreate,
    LogRead,
    MessageCreate,
    MessageRead,
    UserCreate,
    UserRead,
)

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, ReadSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, *, id: UUID) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(self.model.user_id == id))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    # Additional methods like update, delete etc. can be added here.


class CRUDUser(CRUDBase[User, UserCreate, UserRead]):
    pass


class CRUDChat(CRUDBase[Chat, ChatCreate, ChatRead]):
    pass


class CRUDMessage(CRUDBase[Message, MessageCreate, MessageRead]):
    pass


class CRUDLog(CRUDBase[Log, LogCreate, LogRead]):
    async def get_chat_logs(self, db: AsyncSession, *, chat_id: UUID) -> list[Log]:
        result = await db.execute(
            select(self.model)
            .where(self.model.chat_id == chat_id)
            .order_by(self.model.timestamp)
        )
        return list(result.scalars().all())


# Instantiate the CRUD objects for shared use
user = CRUDUser(User)
chat = CRUDChat(Chat)
message = CRUDMessage(Message)
log = CRUDLog(Log)
