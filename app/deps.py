from typing import AsyncGenerator

from .db.database import AsyncSessionLocal


async def get_db_session() -> AsyncGenerator["AsyncSession", None]:
    """FastAPI dependency that yields a database session for each request."""
    async with AsyncSessionLocal() as session:
        yield session
