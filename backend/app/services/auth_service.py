"""
Authentication and authorization service
Handles user registration, login, token management
"""

from datetime import datetime, timedelta
from typing import Optional
import secrets

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User, SubscriptionTier
from app.config import settings


# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for user authentication and authorization"""

    # JWT Configuration
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS = 30

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @classmethod
    def create_access_token(
        cls,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({
            "exp": expire,
            "type": "access"
        })

        encoded_jwt = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt

    @classmethod
    def create_refresh_token(cls, data: dict) -> str:
        """Create a JWT refresh token with longer expiration"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })

        encoded_jwt = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt

    @classmethod
    def verify_token(cls, token: str, token_type: str = "access") -> Optional[dict]:
        """
        Verify and decode a JWT token.
        Returns the payload if valid, None otherwise.
        """
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])

            # Check token type
            if payload.get("type") != token_type:
                return None

            return payload
        except JWTError:
            return None

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.
        Returns the user if authentication successful, None otherwise.
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None
    ) -> User:
        """
        Create a new user account.
        New users get FREE tier with 1 credit.
        """
        hashed_password = AuthService.get_password_hash(password)

        # Generate verification token
        verification_token = secrets.token_urlsafe(32)

        user = User(
            email=email.lower().strip(),
            username=username.strip(),
            hashed_password=hashed_password,
            full_name=full_name.strip() if full_name else None,
            subscription_tier=SubscriptionTier.FREE,
            credits_remaining=1,  # Free tier gets 1 book credit
            verification_token=verification_token
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get a user by email address"""
        return db.query(User).filter(User.email == email.lower()).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get a user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get a user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def verify_email(db: Session, token: str) -> Optional[User]:
        """
        Verify user email using verification token.
        Returns the user if verification successful, None otherwise.
        """
        user = db.query(User).filter(User.verification_token == token).first()
        if not user:
            return None

        user.is_verified = True
        user.verification_token = None
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def create_password_reset_token(db: Session, email: str) -> Optional[str]:
        """
        Create a password reset token for a user.
        Returns the token if user found, None otherwise.
        """
        user = db.query(User).filter(User.email == email.lower()).first()
        if not user:
            return None

        reset_token = secrets.token_urlsafe(32)
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
        db.commit()

        return reset_token

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> Optional[User]:
        """
        Reset user password using reset token.
        Returns the user if successful, None otherwise.
        """
        user = db.query(User).filter(
            User.password_reset_token == token,
            User.password_reset_expires > datetime.utcnow()
        ).first()

        if not user:
            return None

        user.hashed_password = AuthService.get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def update_last_login(db: Session, user: User):
        """Update user's last login timestamp"""
        user.last_login = datetime.utcnow()
        db.commit()

    @staticmethod
    def update_password(db: Session, user: User, new_password: str) -> User:
        """Update user password"""
        user.hashed_password = AuthService.get_password_hash(new_password)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def deactivate_user(db: Session, user: User) -> User:
        """Deactivate a user account"""
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def reactivate_user(db: Session, user: User) -> User:
        """Reactivate a user account"""
        user.is_active = True
        db.commit()
        db.refresh(user)
        return user
