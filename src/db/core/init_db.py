import asyncio
import logging

from core.crud import user
from core.database import AsyncSessionLocal
from core.schemas import UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Initialize database with required initial data."""
    async with AsyncSessionLocal() as db:
        try:
            # Check if we already have users
            result = await user.get_multi(db, limit=1)
            if result:
                logger.info("Database already initialized, skipping")
                return

            # Create initial admin user
            admin_user = UserCreate(
                username="admin",
                email="admin@example.com",
            )
            await user.create(db, obj_in=admin_user)
            logger.info("Created initial admin user")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise


def main() -> None:
    """Main function to run database initialization."""
    logger.info("Creating initial data")
    asyncio.run(init_db())
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
