import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.schemas.user import UserCreate
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.db.database import DATABASE_URL
from app.schemas.user import UserLoginResponse

# Create a new database engine for testing
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def test_user_creation():
    print("Testing user creation and serialization...")
    
    async with AsyncSessionLocal() as session:
        # Create user repository and service
        user_repo = UserRepository(session)
        user_service = UserService(user_repo)

        # Create a test user
        user_data = UserCreate(
            email="test_serialization@example.com",
            username="testserialuser",
            password="password123"
        )

        print(f"\nAttempting to create user with email: {user_data.email}")
        
        # Check if user already exists
        existing_user = await user_service.get_user_by_email(user_data.email)
        if existing_user:
            print(f"User already exists with email: {existing_user.email}")
            # Try to delete the existing user first
            result = await user_repo.delete_user(existing_user.id)
            print(f"Deleted existing user: {result}")
        
        # Create new user
        user = await user_service.create_user(user_data)
        
        if user:
            print(f"User created successfully: {user.email}")
            print(f"User ID: {user.id}")
            
            # Try to serialize the user as would happen in the API response
            try:
                user_response = UserLoginResponse(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                )
                print(f"Serialization successful: {user_response.email}")
                
                # Convert to dict to simulate JSON response
                user_dict = user_response.dict()
                print(f"Dict conversion successful: {user_dict['email']}")
                
            except Exception as e:
                print(f"Serialization error: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print("Failed to create user - returned None")
            
            # Check if user was created despite returning None
            check_user = await user_service.get_user_by_email(user_data.email)
            if check_user:
                print(f"User was created but not returned: {check_user.email}")
            else:
                print("User was not created in the database")

if __name__ == "__main__":
    asyncio.run(test_user_creation())