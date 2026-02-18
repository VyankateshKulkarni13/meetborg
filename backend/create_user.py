import asyncio
import sys
import os

# Add current directory to path to ensure we can import app
sys.path.append(os.getcwd())

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_admin():
    print("Connecting to database...")
    async with AsyncSessionLocal() as db:
        # Check if user exists
        print("Checking for existing 'admin' user...")
        result = await db.execute(select(User).where(User.username == "admin"))
        user = result.scalar_one_or_none()
        
        if user:
            print("User 'admin' already exists.")
            # Update password just in case
            user.hashed_password = get_password_hash("admin")
            await db.commit()
            print("Password reset to 'admin'.")
            return

        print("Creating user 'admin'...")
        new_user = User(
            username="admin",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_superuser=True
        )
        db.add(new_user)
        await db.commit()
        print("User 'admin' created successfully.")
        print("Username: admin")
        print("Password: admin")

if __name__ == "__main__":
    asyncio.run(create_admin())
