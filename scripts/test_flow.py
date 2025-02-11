import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict

import httpx
from sqlalchemy import delete, select

from common.db.connect import AsyncSessionLocal
from src.api.core.utils import check_api_health
from src.common.db.models import Chat, Log, Message, User

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000"


async def cleanup_test_data() -> None:
    """Clean up any existing test data."""
    try:
        async with AsyncSessionLocal() as db:
            # Delete test user and related data (cascading will handle related records)
            await db.execute(delete(User).where(User.email == "test@example.com"))
            await db.commit()
            logger.info("Cleaned up existing test data")
    except Exception as e:
        logger.error(f"Failed to clean up test data: {str(e)}")
        raise


async def create_test_data() -> Dict[str, uuid.UUID]:
    """Create test user and chat in database."""
    try:
        # Clean up any existing test data first
        await cleanup_test_data()

        async with AsyncSessionLocal() as db:
            # Create test user with unique email
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            user = User(
                username=f"test_user_{timestamp}",
                email=f"test_{timestamp}@example.com",
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"Created test user with ID: {user.id}")

            # Create chat
            chat = Chat(user_id=user.id)
            db.add(chat)
            await db.commit()
            await db.refresh(chat)
            logger.info(f"Created test chat with ID: {chat.id}")

            return {"user_id": user.id, "chat_id": chat.id}
    except Exception as e:
        logger.error(f"Failed to create test data: {str(e)}")
        raise


async def send_message(
    chat_id: uuid.UUID, user_id: uuid.UUID, content: str
) -> Dict[str, Any]:
    """Send message through API."""
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "chat_id": str(chat_id),
                "user_id": str(user_id),
                "content": content,
            }
            logger.info(f"Sending message with payload: {payload}")

            response = await client.post(
                f"{API_URL}/api/v1/chat/message",
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Message sent successfully: {result}")
            return result
    except httpx.RequestError as e:
        logger.error(f"Failed to send message - Request error: {str(e)}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Failed to send message - HTTP {e.response.status_code}: {e.response.text}"
        )
        raise


async def check_database() -> None:
    """Check if message and logs were created."""
    try:
        async with AsyncSessionLocal() as db:
            # Check messages
            messages = await db.execute(select(Message))
            messages = list(messages.scalars().all())
            logger.info(f"Found {len(messages)} messages in database")

            print("\nMessages in database:")
            for msg in messages:
                print(f"Content: {msg.content}")
                print(f"User: {msg.user_id}")
                print(f"Chat: {msg.chat_id}")
                print(f"Timestamp: {msg.timestamp}")
                print("---")

            # Check logs
            logs = await db.execute(select(Log))
            logs = list(logs.scalars().all())
            logger.info(f"Found {len(logs)} logs in database")

            print("\nLogs in database:")
            for log in logs:
                print(f"Action: {log.action}")
                print(f"Details: {log.details}")
                print(f"User: {log.user_id}")
                print(f"Chat: {log.chat_id}")
                print(f"Timestamp: {log.timestamp}")
                print("---")

            return len(messages), len(logs)
    except Exception as e:
        logger.error(f"Failed to check database: {str(e)}")
        raise


async def main() -> None:
    """Run the test flow."""
    try:
        # Check API health
        logger.info("Checking API health...")
        if not await check_api_health():
            logger.error("API is not healthy, aborting test")
            return

        # Create test data
        logger.info("Creating test data...")
        ids = await create_test_data()

        # Send test message
        logger.info("Sending test message...")
        await send_message(
            chat_id=ids["chat_id"],
            user_id=ids["user_id"],
            content="Hello, this is a test message!",
        )

        # Check results
        logger.info("Checking database...")
        msg_count, log_count = await check_database()

        # Verify results
        if msg_count == 0:
            logger.warning("No messages found in database!")
        if log_count == 0:
            logger.warning("No logs found in database!")

    except Exception as e:
        logger.error(f"Test flow failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
