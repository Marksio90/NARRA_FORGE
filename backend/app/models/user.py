"""
User model with subscription and credit management for commercial platform
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.database import Base


class SubscriptionTier(str, enum.Enum):
    """Subscription tiers for the platform"""
    FREE = "FREE"
    PRO = "PRO"
    PREMIUM = "PREMIUM"


class User(Base):
    """User model with subscription management"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)

    # Subscription management
    subscription_tier = Column(
        Enum(SubscriptionTier, name='subscription_tier_enum', create_type=False),
        default=SubscriptionTier.FREE,
        nullable=False
    )
    subscription_valid_until = Column(DateTime, nullable=True)
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True)

    # Credits system
    credits_remaining = Column(Integer, default=1, nullable=False)  # Free tier gets 1 credit
    total_credits_purchased = Column(Integer, default=0, nullable=False)

    # Usage tracking
    books_generated = Column(Integer, default=0, nullable=False)
    total_words_generated = Column(Integer, default=0, nullable=False)
    total_cost_incurred = Column(Float, default=0.0, nullable=False)

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    series = relationship("Series", back_populates="user", cascade="all, delete-orphan")

    # Indexes for better query performance
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_username', 'username'),
        Index('idx_users_stripe_customer', 'stripe_customer_id'),
    )

    def has_credits(self) -> bool:
        """Check if user has available credits"""
        return self.credits_remaining > 0

    def deduct_credit(self) -> bool:
        """
        Deduct one credit from user.
        Returns True if successful, False if no credits available.
        """
        if self.credits_remaining > 0:
            self.credits_remaining -= 1
            return True
        return False

    def add_credits(self, amount: int):
        """Add credits to user account"""
        if amount > 0:
            self.credits_remaining += amount
            self.total_credits_purchased += amount

    def is_subscription_active(self) -> bool:
        """Check if subscription is currently active"""
        if self.subscription_tier == SubscriptionTier.FREE:
            return False
        if not self.subscription_valid_until:
            return False
        return datetime.utcnow() < self.subscription_valid_until

    @property
    def monthly_book_limit(self) -> int:
        """Get monthly book generation limit based on tier"""
        limits = {
            SubscriptionTier.FREE: 1,
            SubscriptionTier.PRO: 5,
            SubscriptionTier.PREMIUM: 999999  # Effectively unlimited
        }
        return limits.get(self.subscription_tier, 1)

    @property
    def max_words_per_book(self) -> int:
        """Get maximum words per book based on tier"""
        limits = {
            SubscriptionTier.FREE: 50000,
            SubscriptionTier.PRO: 150000,
            SubscriptionTier.PREMIUM: 200000
        }
        return limits.get(self.subscription_tier, 50000)

    @property
    def can_create_series(self) -> bool:
        """Check if user can create book series"""
        return self.subscription_tier in [SubscriptionTier.PRO, SubscriptionTier.PREMIUM]

    @property
    def has_priority_generation(self) -> bool:
        """Check if user has priority in generation queue"""
        return self.subscription_tier == SubscriptionTier.PREMIUM

    @property
    def can_generate_covers(self) -> bool:
        """Check if user can generate AI covers"""
        return self.subscription_tier in [SubscriptionTier.PRO, SubscriptionTier.PREMIUM]

    def record_book_generation(self, word_count: int, cost: float):
        """Record a completed book generation"""
        self.books_generated += 1
        self.total_words_generated += word_count
        self.total_cost_incurred += cost

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', tier='{self.subscription_tier}')>"


class SubscriptionPlan(Base):
    """Subscription plan definitions for pricing display"""
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    tier = Column(
        Enum(SubscriptionTier, name='subscription_tier_enum', create_type=False),
        nullable=False
    )

    # Pricing
    price_monthly = Column(Float, nullable=False)
    price_yearly = Column(Float, nullable=False)

    # Features
    books_per_month = Column(Integer, nullable=False)
    max_words_per_book = Column(Integer, nullable=False)
    series_support = Column(Boolean, default=False, nullable=False)
    priority_generation = Column(Boolean, default=False, nullable=False)
    cover_generation = Column(Boolean, default=False, nullable=False)
    deep_editing = Column(Boolean, default=False, nullable=False)
    all_export_formats = Column(Boolean, default=False, nullable=False)

    # Stripe integration
    stripe_price_id_monthly = Column(String(255), nullable=True)
    stripe_price_id_yearly = Column(String(255), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<SubscriptionPlan(name='{self.name}', tier='{self.tier}', price=${self.price_monthly}/mo)>"
