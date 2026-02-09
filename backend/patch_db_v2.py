import asyncio
import sys
import os

# Add parent dir to path so we can import 'app'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.db.session import engine
from sqlalchemy import text

async def patch():
    print("Patching database...")
    async with engine.begin() as conn:
        print("Checking session_cookies column...")
        await conn.execute(text("ALTER TABLE platforms ADD COLUMN IF NOT EXISTS session_cookies JSONB;"))
        print("Checking browser_session_state column...")
        await conn.execute(text("ALTER TABLE platforms ADD COLUMN IF NOT EXISTS browser_session_state JSONB;"))
        print("Checking session_valid_until column...")
        await conn.execute(text("ALTER TABLE platforms ADD COLUMN IF NOT EXISTS session_valid_until TIMESTAMP;"))
        print("Checking error_message column...")
        await conn.execute(text("ALTER TABLE platforms ADD COLUMN IF NOT EXISTS error_message TEXT;"))
    print("Database patched successfully.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(patch())
