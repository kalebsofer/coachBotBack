from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from db.core.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
