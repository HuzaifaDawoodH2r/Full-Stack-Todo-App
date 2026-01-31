import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.user import User
from app.db.database import DATABASE_URL

# Create a new database engine for testing
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def list_users():
    print("Listing all users in the database...")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        if users:
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"  ID: {user.id}")
                print(f"  Email: {user.email}")
                print(f"  Username: {user.username}")
                print(f"  Is Active: {user.is_active}")
                print(f"  Created At: {user.created_at}")
                print(f"  Updated At: {user.updated_at}")
                print("---")
        else:
            print("No users found in the database.")

if __name__ == "__main__":
    asyncio.run(list_users())