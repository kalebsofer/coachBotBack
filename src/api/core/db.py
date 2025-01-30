from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from db.core.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
