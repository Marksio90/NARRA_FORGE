"""
JWT token generation and validation.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError

from api.config import get_settings


class TokenData(BaseModel):
    """Data stored in JWT token."""
    user_id: str
    email: str
    subscription_tier: str
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None


class TokenPair(BaseModel):
    """Access token + refresh token pair."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


def create_access_token(
    user_id: str,
    email: str,
    subscription_tier: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a new JWT access token.
    
    Args:
        user_id: User's unique identifier
        email: User's email
        subscription_tier: User's subscription tier (FREE, PRO, ENTERPRISE)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    settings = get_settings()
    
    # Set expiration
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    
    # Create token payload
    payload: Dict[str, Any] = {
        "sub": user_id,  # Subject (user ID)
        "email": email,
        "subscription_tier": subscription_tier,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }
    
    # Encode token
    encoded_jwt = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def create_refresh_token(
    user_id: str,
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a new JWT refresh token.
    
    Args:
        user_id: User's unique identifier
        email: User's email
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT refresh token string
    """
    settings = get_settings()
    
    # Set expiration (longer for refresh tokens)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )
    
    # Create token payload (minimal data for refresh)
    payload: Dict[str, Any] = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    }
    
    # Encode token
    encoded_jwt = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def create_token_pair(
    user_id: str,
    email: str,
    subscription_tier: str
) -> TokenPair:
    """
    Create both access and refresh tokens.
    
    Args:
        user_id: User's unique identifier
        email: User's email
        subscription_tier: User's subscription tier
        
    Returns:
        TokenPair with access and refresh tokens
    """
    settings = get_settings()
    
    access_token = create_access_token(user_id, email, subscription_tier)
    refresh_token = create_refresh_token(user_id, email)
    
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60
    )


def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token to verify
        token_type: Expected token type ("access" or "refresh")
        
    Returns:
        TokenData if valid, None if invalid
        
    Raises:
        JWTError: If token is invalid or expired
    """
    settings = get_settings()
    
    try:
        # Decode token
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        # Check token type
        if payload.get("type") != token_type:
            raise JWTError(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
        
        # Extract data
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        subscription_tier: str = payload.get("subscription_tier", "FREE")
        exp = payload.get("exp")
        iat = payload.get("iat")
        
        if user_id is None or email is None:
            raise JWTError("Invalid token payload")
        
        # Convert timestamps
        exp_dt = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else None
        iat_dt = datetime.fromtimestamp(iat, tz=timezone.utc) if iat else None
        
        return TokenData(
            user_id=user_id,
            email=email,
            subscription_tier=subscription_tier,
            exp=exp_dt,
            iat=iat_dt
        )
        
    except (JWTError, ValidationError) as e:
        raise JWTError(f"Token verification failed: {str(e)}")


def decode_token_payload(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT token without verification (for debugging).
    
    Args:
        token: The JWT token to decode
        
    Returns:
        Decoded payload dict or None if invalid
    """
    try:
        return jwt.decode(token, options={"verify_signature": False})
    except JWTError:
        return None
