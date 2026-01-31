from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_session
from app.schemas.user import UserCreate, UserLogin, UserLoginResponse
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from typing import Dict

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_user_service(db_session: AsyncSession = Depends(get_async_session)):
    """Dependency to get the user service with repository"""
    user_repo = UserRepository(db_session)
    return UserService(user_repo)


@router.post("/signup", response_model=UserLoginResponse, status_code=201)
async def signup(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """Register a new user"""
    try:
        print(f"DEBUG: Received signup request for email: {user_create.email}, username: {user_create.username}")

        # Check if user already exists
        existing_user = await user_service.get_user_by_email(user_create.email)
        if existing_user:
            print(f"DEBUG: User with email {user_create.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )

        print(f"DEBUG: No existing user with email {user_create.email}")

        # Check if username already exists
        existing_user_by_username = await user_service.get_user_by_username(user_create.username)
        if existing_user_by_username:
            print(f"DEBUG: User with username {user_create.username} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this username already exists"
            )

        print(f"DEBUG: No existing user with username {user_create.username}")

        # Create new user
        print(f"DEBUG: Attempting to create user with email: {user_create.email}")
        user = await user_service.create_user(user_create)
        print(f"DEBUG: User creation result: {user}")

        if not user:
            print(f"DEBUG: Failed to create user - returned None")

            # Let's double-check if the user was actually created despite returning None
            check_user = await user_service.get_user_by_email(user_create.email)
            if check_user:
                print(f"DEBUG: User was created but not returned: {check_user.email}")
            else:
                print(f"DEBUG: User was not created in the database")

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )

        print(f"DEBUG: User created successfully: {user.email}")

        # Extract user data to avoid potential lazy-loading issues when session closes
        user_data = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }

        # Return user info (without password)
        return UserLoginResponse(**user_data)
    except HTTPException:
        print(f"DEBUG: HTTPException caught")
        raise
    except Exception as e:
        print(f"DEBUG: Unexpected exception: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {str(e)}"
        )


@router.post("/signin", response_model=UserLoginResponse)
async def signin(
    user_login: UserLogin,
    user_service: UserService = Depends(get_user_service)
):
    """Authenticate a user and return user info"""
    try:
        # Authenticate user
        user = await user_service.authenticate_user(user_login.email, user_login.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )

        # Extract user data to avoid potential lazy-loading issues when session closes
        user_data = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }

        # Return user info (without password)
        return UserLoginResponse(**user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}"
        )


@router.post("/signout")
async def signout():
    """Simple signout endpoint - no session management needed for this basic implementation"""
    return {"message": "Successfully signed out"}