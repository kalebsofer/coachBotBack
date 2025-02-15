import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Please check your .env file.")


def get_sync_url(url: str) -> str:
    """Convert async URL to sync URL for migrations"""
    url = url.replace("localhost", "postgres")  # Ensure correct host
    if "postgresql+asyncpg://" in url:
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    if "postgresql://" in url:
        return url.replace("postgresql://", "postgresql+psycopg2://")
    return url


def get_async_url(url: str) -> str:
    """Convert URL to async URL for application"""
    url = url.replace("localhost", "postgres")  # Ensure correct host
    if "postgresql+psycopg2://" in url:
        return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
    if "postgresql://" in url:
        return url.replace("postgresql://", "postgresql+asyncpg://")
    return url


# For application (async)
engine = create_async_engine(
    get_async_url(DATABASE_URL),
    echo=True,
    pool_pre_ping=True,  # This will check connection before using it
    pool_recycle=300,  # Recycle connections every 5 minutes
    pool_size=5,  # Maintain up to 5 connections
    max_overflow=10,  # Allow up to 10 additional connections
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


async def wait_for_db(max_retries=5, retry_interval=5):
    """Wait for database to become available"""
    for attempt in range(max_retries):
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
                return
        except OperationalError as e:
            if attempt == max_retries - 1:
                raise
            logging.warning(
                f"Database connection attempt {attempt + 1} failed, retrying in {retry_interval} seconds..."
            )
            await asyncio.sleep(retry_interval)
