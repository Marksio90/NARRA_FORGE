"""
FastAPI dependencies for authentication and authorization.
"""

from typing import Optional, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.models.base import get_db
from api.models.user import User
from api.auth.jwt import verify_token, TokenData
from jose import JWTError


# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Authorization Bearer token
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token
        token = credentials.credentials
        
        # Verify token
        token_data: TokenData = verify_token(token, token_type="access")
        
        if token_data is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    stmt = select(User).where(User.id == token_data.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get the current active user (must be active, not disabled).
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        Active user object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    Get the current verified user (must be active and verified).
    
    Args:
        current_user: The current active user
        
    Returns:
        Verified user object
        
    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return current_user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    Get the current superuser (must be active and superuser).
    
    Args:
        current_user: The current active user
        
    Returns:
        Superuser object
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def require_subscription_tier(
    required_tier: str
):
    """
    Dependency factory for requiring a minimum subscription tier.
    
    Args:
        required_tier: Minimum tier required (FREE, PRO, ENTERPRISE)
        
    Returns:
        FastAPI dependency function
    """
    tier_hierarchy = {
        "FREE": 0,
        "PRO": 1,
        "ENTERPRISE": 2
    }
    
    async def check_tier(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> User:
        """Check if user has required subscription tier."""
        user_tier_level = tier_hierarchy.get(current_user.subscription_tier.value, 0)
        required_tier_level = tier_hierarchy.get(required_tier, 0)
        
        if user_tier_level < required_tier_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Subscription tier {required_tier} or higher required"
            )
        
        return current_user
    
    return check_tier


# Optional authentication (returns None if not authenticated)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get the current user if authenticated, otherwise None.
    
    Useful for endpoints that have different behavior for authenticated users
    but don't require authentication.
    
    Args:
        credentials: Optional HTTP Authorization Bearer token
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        token_data: TokenData = verify_token(token, token_type="access")
        
        if token_data is None:
            return None
        
        stmt = select(User).where(User.id == token_data.user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        return user if user and user.is_active else None
        
    except (JWTError, Exception):
        return None
