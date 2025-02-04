import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Ensure DATABASE_URL is set in your environment, for example:
# DATABASE_URL=postgresql+asyncpg://postgres:postgrespword@database:5432/coach_bot
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgrespword@database:5432/coach_bot")

# Create an asynchronous engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a sessionmaker for AsyncSession
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# A dependency-like async generator to be used with `async with`
async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session 