import asyncio
from sqlalchemy import text
from app.db.database import engine

async def verify():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;"))
        tables = [row[0] for row in res.fetchall()]
        print("Actual tables in the connected database (public schema):")
        print(tables if tables else "[]  <-- NO TABLES FOUND")
        if "repositories" in tables:
            print("\n✓ SUCCESS: 'repositories' table exists in the DB.")
        else:
            print("\n✗ 'repositories' table does NOT exist in this database.")

asyncio.run(verify())
