import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.schemas.user import UserCreate
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.db.database import DATABASE_URL
from app.routers.auth import get_user_service
from contextlib import asynccontextmanager

# Create a new database engine for testing
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session

async def test_api_flow():
    print("Testing the exact API flow...")
    
    # Simulate the dependency injection
    async with get_async_session() as session:
        user_service = UserService(UserRepository(session))
        
        # Create a test user
        user_data = UserCreate(
            email="api_flow_test@example.com",
            username="apiflowtest",
            password="password123"
        )

        print(f"Step 1: Checking if user with email '{user_data.email}' already exists...")
        existing_user = await user_service.get_user_by_email(user_data.email)
        if existing_user:
            print(f"Found existing user with email: {existing_user.email}")
            return
        else:
            print("No existing user with this email")

        print(f"Step 2: Checking if user with username '{user_data.username}' already exists...")
        existing_user = await user_service.get_user_by_username(user_data.username)
        if existing_user:
            print(f"Found existing user with username: {existing_user.username}")
            return
        else:
            print("No existing user with this username")

        print(f"Step 3: Attempting to create user with email: {user_data.email}")
        user = await user_service.create_user(user_data)
        
        if user:
            print(f"SUCCESS: User created successfully: {user.email}")
            print(f"User ID: {user.id}")
        else:
            print("FAILED: User creation returned None")
            
            # Let's try to see if there were any exceptions that were silently handled
            print("Trying to create user again with more detailed error checking...")
            try:
                user = await user_service.create_user(user_data)
                print(f"Second attempt result: {user}")
            except Exception as e:
                print(f"Exception during second attempt: {str(e)}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api_flow())