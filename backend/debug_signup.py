import asyncio
import traceback
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from app.models.user import User
from app.schemas.user import UserCreate
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.db.database import DATABASE_URL

# Create a new database engine for testing
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def debug_user_creation():
    print("Starting user creation debug...")

    # Check if the users table exists and its structure
    async with engine.connect() as conn:
        def inspect_db(sync_conn):
            inspector = inspect(sync_conn)
            tables = inspector.get_table_names()
            return tables, inspector

        tables, inspector = await conn.run_sync(inspect_db)
        print(f"Tables in database: {tables}")

        if 'users' in tables:
            def get_columns(sync_conn):
                inspector = inspect(sync_conn)
                return inspector.get_columns('users')

            columns = await conn.run_sync(get_columns)
            print("Users table structure:")
            for col in columns:
                print(f"  {col['name']}: {col['type']} (nullable: {col['nullable']})")
        else:
            print("ERROR: Users table does not exist!")
            return

    async with AsyncSessionLocal() as session:
        
        # Create user repository and service
        user_repo = UserRepository(session)
        user_service = UserService(user_repo)

        # Create a test user
        user_data = UserCreate(
            email="debug_test@example.com",
            username="debuguser",
            password="password123"
        )

        print("\nAttempting to create user...")
        try:
            user = await user_service.create_user(user_data)
            
            if user:
                print(f"User created successfully: {user.email}")
                print(f"User ID: {user.id}")
            else:
                print("Failed to create user - returned None")
                
                # Check if user already exists
                existing_user = await user_service.get_user_by_email("debug_test@example.com")
                if existing_user:
                    print(f"User already exists with email: {existing_user.email}")
                    
                # Check if username already exists
                existing_user = await user_service.get_user_by_username("debuguser")
                if existing_user:
                    print(f"User already exists with username: {existing_user.username}")
                    
        except Exception as e:
            print(f"Exception during user creation: {str(e)}")
            print("Full traceback:")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_user_creation())