import os
import asyncio
import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Please check your .env file.")

def get_sync_url(url: str) -> str:
    """Convert an async URL to a sync URL for migrations."""
    url = url.replace("localhost", "postgres")
    if 'postgresql+asyncpg://' in url:
        return url.replace('postgresql+asyncpg://', 'postgresql+psycopg2://')
    if 'postgresql://' in url:
        return url.replace('postgresql://', 'postgresql+psycopg2://')
    return url

def get_async_url(url: str) -> str:
    """Convert a URL to an async-friendly URL for application use."""
    url = url.replace("localhost", "postgres")
    if 'postgresql+psycopg2://' in url:
        return url.replace('postgresql+psycopg2://', 'postgresql+asyncpg://')
    if 'postgresql://' in url:
        return url.replace('postgresql://', 'postgresql+asyncpg://')
    return url

engine = create_async_engine(
    get_async_url(DATABASE_URL),
    echo=True,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager that yields a database session and handles commit/rollback."""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

# NEW: Dependency function to use with FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency function that yields a database session."""
    async with get_session() as session:
        yield session

async def wait_for_db(max_retries: int = 5, retry_interval: int = 5):
    """Wait for the database to become available."""
    for attempt in range(max_retries):
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
                return
        except OperationalError as e:
            if attempt == max_retries - 1:
                raise
            logging.warning(f"Database connection attempt {attempt + 1} failed, retrying in {retry_interval} seconds...")
            await asyncio.sleep(retry_interval)
