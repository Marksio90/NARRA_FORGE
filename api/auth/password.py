"""
Password hashing and verification using bcrypt.
"""

from passlib.context import CryptContext

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    
    Args:
        password: The plaintext password
        
    Returns:
        The hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.
    
    Args:
        plain_password: The plaintext password to verify
        hashed_password: The hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if a hashed password needs to be rehashed with updated parameters.
    
    Args:
        hashed_password: The hashed password to check
        
    Returns:
        True if needs rehashing, False otherwise
    """
    return pwd_context.needs_update(hashed_password)
