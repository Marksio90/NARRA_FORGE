"""
Authentication Routes.

Handles user authentication, registration, and OAuth2 flows.
"""

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.models.base import get_db
from api.models.user import User, SubscriptionTier
from api.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenRefreshRequest,
    AuthResponse,
    UserResponse,
    MessageResponse
)
from api.auth import hash_password, verify_password, create_token_pair, verify_token
from jose import JWTError


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Register a new user with email and password.

    Password requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit

    Returns JWT tokens and user information.
    """
    # Check if user already exists
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    new_user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
        is_active=True,
        is_verified=False,  # Email verification required
        is_superuser=False,
        subscription_tier=SubscriptionTier.FREE,
        monthly_generation_limit=5,  # Free tier default
        monthly_generations_used=0,
        monthly_cost_limit_usd=0.0,
        monthly_cost_used_usd=0.0
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Generate JWT tokens
    token_pair = create_token_pair(
        user_id=new_user.id,
        email=new_user.email,
        subscription_tier=new_user.subscription_tier.value
    )

    # Create response
    user_response = UserResponse.model_validate(new_user)

    return AuthResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type=token_pair.token_type,
        expires_in=token_pair.expires_in,
        user=user_response
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: UserLoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Login with email and password.

    Returns JWT tokens and user information.
    """
    # Find user by email
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    # Update last login timestamp
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)

    # Generate JWT tokens
    token_pair = create_token_pair(
        user_id=user.id,
        email=user.email,
        subscription_tier=user.subscription_tier.value
    )

    # Create response
    user_response = UserResponse.model_validate(user)

    return AuthResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type=token_pair.token_type,
        expires_in=token_pair.expires_in,
        user=user_response
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Refresh access token using refresh token.

    Returns new JWT token pair.
    """
    try:
        # Verify refresh token
        token_data = verify_token(request.refresh_token, token_type="refresh")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Get user from database
    stmt = select(User).where(User.id == token_data.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    # Generate new token pair
    token_pair = create_token_pair(
        user_id=user.id,
        email=user.email,
        subscription_tier=user.subscription_tier.value
    )

    # Create response
    user_response = UserResponse.model_validate(user)

    return AuthResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type=token_pair.token_type,
        expires_in=token_pair.expires_in,
        user=user_response
    )


@router.get("/oauth/google", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def google_oauth():
    """
    Google OAuth2 login.

    TODO: Implement Google OAuth2 flow
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google OAuth not yet implemented"
    )


@router.get("/oauth/github", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def github_oauth():
    """
    GitHub OAuth2 login.

    TODO: Implement GitHub OAuth2 flow
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="GitHub OAuth not yet implemented"
    )
