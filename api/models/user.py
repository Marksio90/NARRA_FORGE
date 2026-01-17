"""
User model for authentication and account management.
"""

import uuid
from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import Boolean, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base


class SubscriptionTier(str, enum.Enum):
    """Subscription tier levels."""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class User(Base):
    """
    User account model.

    Features:
    - Email/password authentication
    - OAuth providers (Google, GitHub)
    - Subscription tiers
    - Usage limits
    """

    __tablename__ = "users"

    # Override id to use UUID
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Null for OAuth users
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # OAuth
    oauth_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "google", "github", etc.
    oauth_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    # Profile
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Subscription
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        SQLEnum(SubscriptionTier),
        default=SubscriptionTier.FREE,
        nullable=False
    )
    subscription_ends_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Usage limits (reset monthly)
    monthly_generation_limit: Mapped[int] = mapped_column(default=5, nullable=False)  # Free: 5, Pro: 50, Enterprise: unlimited
    monthly_generations_used: Mapped[int] = mapped_column(default=0, nullable=False)
    monthly_cost_limit_usd: Mapped[float] = mapped_column(default=10.0, nullable=False)
    monthly_cost_used_usd: Mapped[float] = mapped_column(default=0.0, nullable=False)

    # Timestamps
    last_login_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships (will be added when other models are defined)
    # projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    # usage_logs = relationship("UsageLog", back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.subscription_tier.value})>"

    @property
    def can_generate(self) -> bool:
        """Check if user can generate more narratives this month."""
        if self.subscription_tier == SubscriptionTier.ENTERPRISE:
            return True  # Unlimited
        return self.monthly_generations_used < self.monthly_generation_limit

    @property
    def remaining_generations(self) -> Optional[int]:
        """Get remaining generations for this month."""
        if self.subscription_tier == SubscriptionTier.ENTERPRISE:
            return None  # Unlimited
        return max(0, self.monthly_generation_limit - self.monthly_generations_used)

    def reset_monthly_usage(self) -> None:
        """Reset monthly usage counters (called monthly by cron)."""
        self.monthly_generations_used = 0
        self.monthly_cost_used_usd = 0.0
