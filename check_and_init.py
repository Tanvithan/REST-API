import asyncio
from app.db.database import engine
from app.db.models import Base

async def main():
    print("Starting table creation...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("create_all completed without exception.")
    print("Tables that should exist:", list(Base.metadata.tables.keys()))

asyncio.run(main())
