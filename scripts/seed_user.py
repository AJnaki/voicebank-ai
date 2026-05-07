"""
Seed a test user into the database.
Usage: python scripts/seed_user.py
"""
import asyncio
import bcrypt
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import AsyncSessionLocal, create_tables
from app.models.user import User


async def seed():
    await create_tables()

    pin = "123456"
    pin_hash = bcrypt.hashpw(pin.encode(), bcrypt.gensalt(rounds=12)).decode()

    async with AsyncSessionLocal() as db:
        user = User(
            first_name="John",
            last_name="Smith",
            phone_number="+15550001234",
            pin_hash=pin_hash,
            account_number="****4821",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"Created user: {user.full_name} (id={user.id}), PIN: {pin}")


if __name__ == "__main__":
    asyncio.run(seed())
