import asyncio
from sqlalchemy import text
from app.db.database import engine

async def inspect():
    async with engine.connect() as conn:
        res = await conn.execute(text("""
            SELECT id, external_id, full_name, stargazers_count, updated_at, fetched_at 
            FROM repositories 
            ORDER BY id;
        """))
        rows = res.fetchall()
        print(f"Total rows in repositories table: {len(rows)}")
        if rows:
            print("\nCurrent records:")
            for r in rows:
                print(f"  id={r[0]}, external_id={r[1]}, stars={r[3]}, updated_at={r[4]}, fetched_at={r[5]}")
        else:
            print("  (table is empty)")

asyncio.run(inspect())
