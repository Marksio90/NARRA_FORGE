"""
Authentication module for NARRA_FORGE API.

Exports:
- Password hashing: hash_password, verify_password
- JWT tokens: create_token_pair, verify_token
- Dependencies: get_current_user, get_current_active_user, etc.
"""

from api.auth.password import hash_password, verify_password, needs_rehash
from api.auth.jwt import (
    create_access_token,
    create_refresh_token,
    create_token_pair,
    verify_token,
    decode_token_payload,
    TokenData,
    TokenPair
)
from api.auth.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_verified_user,
    get_current_superuser,
    get_current_user_optional,
    require_subscription_tier,
    security
)

__all__ = [
    # Password
    "hash_password",
    "verify_password",
    "needs_rehash",
    
    # JWT
    "create_access_token",
    "create_refresh_token",
    "create_token_pair",
    "verify_token",
    "decode_token_payload",
    "TokenData",
    "TokenPair",
    
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "get_current_verified_user",
    "get_current_superuser",
    "get_current_user_optional",
    "require_subscription_tier",
    "security",
]
