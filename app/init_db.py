import asyncio

from .db.database import engine
from .db.models import Base


async def init_db() -> None:
    """Create all database tables defined in the ORM models."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())
