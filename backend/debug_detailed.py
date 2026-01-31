import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.schemas.user import UserCreate
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.db.database import DATABASE_URL

# Create a new database engine for testing
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def debug_user_creation_detailed():
    print("Starting detailed user creation debug...")
    
    async with AsyncSessionLocal() as session:
        # Create user repository and service
        user_repo = UserRepository(session)
        user_service = UserService(user_repo)

        # Create a test user
        user_data = UserCreate(
            email="debug_test2@example.com",
            username="debuguser2",
            password="password123"
        )

        print(f"\nChecking if user with email '{user_data.email}' already exists...")
        existing_user = await user_service.get_user_by_email(user_data.email)
        if existing_user:
            print(f"Found existing user with email: {existing_user.email}")
        else:
            print("No existing user with this email")
        
        print(f"\nChecking if user with username '{user_data.username}' already exists...")
        existing_user = await user_service.get_user_by_username(user_data.username)
        if existing_user:
            print(f"Found existing user with username: {existing_user.username}")
        else:
            print("No existing user with this username")
        
        print("\nAttempting to create user...")
        try:
            user = await user_service.create_user(user_data)
            
            if user:
                print(f"User created successfully: {user.email}")
                print(f"User ID: {user.id}")
            else:
                print("Failed to create user - returned None")
                
        except Exception as e:
            print(f"Exception during user creation: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_user_creation_detailed())