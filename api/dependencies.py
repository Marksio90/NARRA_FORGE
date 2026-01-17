"""
Common FastAPI Dependencies.

Provides reusable dependency injection for routes.
"""

from typing import Optional, AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import settings, get_settings, APISettings
from api.models.base import get_db
from api.models.user import User


# Security
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: Bearer token from Authorization header
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    # TODO: Implement JWT token verification
    # For now, raise 501 Not Implemented
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not yet implemented"
    )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (not disabled).

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current verified user (email verified).

    Args:
        current_user: Current active user

    Returns:
        User: Current verified user

    Raises:
        HTTPException: If user email is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current superuser (admin).

    Args:
        current_user: Current active user

    Returns:
        User: Current superuser

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required"
        )
    return current_user


def get_api_settings() -> APISettings:
    """
    Get API settings dependency.

    Returns:
        APISettings: API configuration settings
    """
    return get_settings()


async def check_rate_limit(
    user: User = Depends(get_current_user)
) -> None:
    """
    Check rate limit for current user.

    Args:
        user: Current authenticated user

    Raises:
        HTTPException: If rate limit exceeded
    """
    # TODO: Implement rate limiting with Redis
    # For now, pass through
    pass


async def check_generation_limit(
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Check if user can generate more narratives.

    Args:
        user: Current active user
        db: Database session

    Raises:
        HTTPException: If generation limit exceeded
    """
    if not user.can_generate:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Monthly generation limit reached ({user.monthly_generation_limit}). "
                   f"Please upgrade your subscription."
        )


async def check_cost_limit(
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Check if user has exceeded cost limit.

    Args:
        user: Current active user
        db: Database session

    Raises:
        HTTPException: If cost limit exceeded
    """
    if user.is_over_cost_limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Monthly cost limit reached (${user.monthly_cost_limit_usd}). "
                   f"Please upgrade your subscription."
        )
