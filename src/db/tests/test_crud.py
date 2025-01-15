import uuid
from typing import AsyncGenerator

import pytest
from app.crud import chat, log, message, user
from app.database import Base
from app.schemas import ChatCreate, LogCreate, MessageCreate, UserCreate
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Create a clean database for each test."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = AsyncSession(engine, expire_on_commit=False)
    try:
        yield async_session
    finally:
        await async_session.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.fixture
async def test_user(db: AsyncSession) -> dict:
    """Create a test user."""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
    )
    db_user = await user.create(db, obj_in=user_data)
    return {"id": db_user.id, "data": user_data}


@pytest.fixture
async def test_chat(db: AsyncSession, test_user: dict) -> dict:
    """Create a test chat."""
    chat_data = ChatCreate(user_id=test_user["id"])
    db_chat = await chat.create(db, obj_in=chat_data)
    return {"id": db_chat.id, "data": chat_data}


class TestUserCRUD:
    """Test user CRUD operations."""

    async def test_create_user(self, db: AsyncSession):
        """Test user creation."""
        user_data = UserCreate(
            username="newuser",
            email="new@example.com",
        )
        db_user = await user.create(db, obj_in=user_data)
        assert db_user.username == user_data.username
        assert db_user.email == user_data.email
        assert isinstance(db_user.id, uuid.UUID)

    async def test_get_user(self, db: AsyncSession, test_user: dict):
        """Test getting a user by ID."""
        db_user = await user.get(db, id=test_user["id"])
        assert db_user is not None
        assert db_user.id == test_user["id"]
        assert db_user.email == test_user["data"].email

    async def test_get_user_by_email(self, db: AsyncSession, test_user: dict):
        """Test getting a user by email."""
        db_user = await user.get_by_email(db, email=test_user["data"].email)
        assert db_user is not None
        assert db_user.id == test_user["id"]

    async def test_get_non_existent_user(self, db: AsyncSession):
        """Test getting a non-existent user."""
        non_existent_id = uuid.uuid4()
        db_user = await user.get(db, id=non_existent_id)
        assert db_user is None


class TestChatCRUD:
    """Test chat CRUD operations."""

    async def test_create_chat(self, db: AsyncSession, test_user: dict):
        """Test chat creation."""
        chat_data = ChatCreate(user_id=test_user["id"])
        db_chat = await chat.create(db, obj_in=chat_data)
        assert db_chat.user_id == test_user["id"]
        assert isinstance(db_chat.id, uuid.UUID)

    async def test_get_user_chats(self, db: AsyncSession, test_chat: dict):
        """Test getting all chats for a user."""
        chats = await chat.get_user_chats(db, user_id=test_chat["data"].user_id)
        assert len(chats) == 1
        assert chats[0].id == test_chat["id"]


class TestMessageCRUD:
    """Test message CRUD operations."""

    async def test_create_message(
        self, db: AsyncSession, test_chat: dict, test_user: dict
    ):
        """Test message creation."""
        message_data = MessageCreate(
            chat_id=test_chat["id"],
            sender_id=test_user["id"],
            content="Test message",
        )
        db_message = await message.create(db, obj_in=message_data)
        assert db_message.content == message_data.content
        assert db_message.chat_id == test_chat["id"]
        assert db_message.sender_id == test_user["id"]

    async def test_get_chat_messages(
        self, db: AsyncSession, test_chat: dict, test_user: dict
    ):
        """Test getting all messages in a chat."""
        # Create two messages
        message_data1 = MessageCreate(
            chat_id=test_chat["id"],
            sender_id=test_user["id"],
            content="Message 1",
        )
        message_data2 = MessageCreate(
            chat_id=test_chat["id"],
            sender_id=test_user["id"],
            content="Message 2",
        )
        await message.create(db, obj_in=message_data1)
        await message.create(db, obj_in=message_data2)

        messages = await message.get_chat_messages(db, chat_id=test_chat["id"])
        assert len(messages) == 2
        assert messages[0].content == "Message 1"
        assert messages[1].content == "Message 2"


class TestLogCRUD:
    """Test log CRUD operations."""

    async def test_create_log(self, db: AsyncSession, test_chat: dict, test_user: dict):
        """Test log creation."""
        log_data = LogCreate(
            user_id=test_user["id"],
            chat_id=test_chat["id"],
            action="test_action",
            details="Test details",
        )
        db_log = await log.create(db, obj_in=log_data)
        assert db_log.action == log_data.action
        assert db_log.details == log_data.details

    async def test_get_chat_logs(
        self, db: AsyncSession, test_chat: dict, test_user: dict
    ):
        """Test getting all logs for a chat."""
        # Create two logs
        log_data1 = LogCreate(
            user_id=test_user["id"],
            chat_id=test_chat["id"],
            action="action1",
        )
        log_data2 = LogCreate(
            user_id=test_user["id"],
            chat_id=test_chat["id"],
            action="action2",
        )
        await log.create(db, obj_in=log_data1)
        await log.create(db, obj_in=log_data2)

        logs = await log.get_chat_logs(db, chat_id=test_chat["id"])
        assert len(logs) == 2
        assert logs[0].action == "action1"
        assert logs[1].action == "action2"
