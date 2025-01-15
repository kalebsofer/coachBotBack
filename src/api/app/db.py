from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.app.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
