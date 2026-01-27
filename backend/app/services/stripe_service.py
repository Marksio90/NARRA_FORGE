"""
Stripe payment integration service
Handles subscriptions, one-time purchases, and webhook processing
"""

import stripe
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

from app.config import settings
from app.models.user import User, SubscriptionTier


logger = logging.getLogger(__name__)


class StripeService:
    """Service for Stripe payment processing"""

    # Pricing configuration
    SUBSCRIPTION_PRICES = {
        SubscriptionTier.PRO: {
            "monthly": 29.00,
            "yearly": 290.00,  # ~17% discount
        },
        SubscriptionTier.PREMIUM: {
            "monthly": 79.00,
            "yearly": 790.00,  # ~17% discount
        }
    }

    # Credit pricing
    CREDIT_PRICE = 15.00  # $15 per book credit

    # Credit packs with discounts
    CREDIT_PACKS = {
        1: {"credits": 1, "price": 15.00, "discount": 0},
        5: {"credits": 5, "price": 65.00, "discount": 13},  # $13/credit
        10: {"credits": 10, "price": 110.00, "discount": 27},  # $11/credit
    }

    # Tier features for credits
    TIER_CREDITS = {
        SubscriptionTier.FREE: 1,
        SubscriptionTier.PRO: 5,
        SubscriptionTier.PREMIUM: 999999,  # Unlimited
    }

    def __init__(self):
        """Initialize Stripe with API key"""
        self.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
        self.webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)

        if self.api_key:
            stripe.api_key = self.api_key
        else:
            logger.warning("STRIPE_SECRET_KEY not configured. Payment features disabled.")

    def is_configured(self) -> bool:
        """Check if Stripe is properly configured"""
        return self.api_key is not None

    def create_customer(self, user: User) -> str:
        """
        Create a Stripe customer for a user.
        Returns the Stripe customer ID.
        """
        if not self.is_configured():
            raise ValueError("Stripe is not configured")

        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name or user.username,
                metadata={
                    "user_id": str(user.id),
                    "username": user.username
                }
            )
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise

    def get_or_create_customer(self, db: Session, user: User) -> str:
        """
        Get existing Stripe customer ID or create a new one.
        Updates user record with customer ID if created.
        """
        if user.stripe_customer_id:
            return user.stripe_customer_id

        customer_id = self.create_customer(user)
        user.stripe_customer_id = customer_id
        db.commit()

        return customer_id

    def create_subscription_checkout(
        self,
        db: Session,
        user: User,
        tier: SubscriptionTier,
        billing_period: str = "monthly"
    ) -> str:
        """
        Create a Stripe checkout session for subscription.
        Returns the checkout URL.
        """
        if not self.is_configured():
            raise ValueError("Stripe is not configured")

        if tier == SubscriptionTier.FREE:
            raise ValueError("Cannot subscribe to FREE tier")

        if tier not in self.SUBSCRIPTION_PRICES:
            raise ValueError(f"Invalid subscription tier: {tier}")

        if billing_period not in ["monthly", "yearly"]:
            raise ValueError("Billing period must be 'monthly' or 'yearly'")

        # Ensure customer exists
        customer_id = self.get_or_create_customer(db, user)

        # Get price
        price = self.SUBSCRIPTION_PRICES[tier][billing_period]

        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'NarraForge {tier.value} - {billing_period.title()}',
                            'description': self._get_tier_description(tier),
                        },
                        'unit_amount': int(price * 100),  # Amount in cents
                        'recurring': {
                            'interval': 'month' if billing_period == 'monthly' else 'year'
                        },
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f"{settings.FRONTEND_URL}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/subscription/cancel",
                metadata={
                    'user_id': str(user.id),
                    'tier': tier.value,
                    'billing_period': billing_period,
                    'type': 'subscription'
                }
            )

            return session.url

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise

    def create_credit_purchase_checkout(
        self,
        db: Session,
        user: User,
        pack_size: int = 1
    ) -> str:
        """
        Create a Stripe checkout session for credit purchase.
        Returns the checkout URL.
        """
        if not self.is_configured():
            raise ValueError("Stripe is not configured")

        if pack_size not in self.CREDIT_PACKS:
            raise ValueError(f"Invalid pack size. Available: {list(self.CREDIT_PACKS.keys())}")

        pack = self.CREDIT_PACKS[pack_size]

        # Ensure customer exists
        customer_id = self.get_or_create_customer(db, user)

        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'NarraForge Book Credits ({pack["credits"]} credits)',
                            'description': f'Generate {pack["credits"]} AI-powered books',
                        },
                        'unit_amount': int(pack["price"] * 100),  # Amount in cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{settings.FRONTEND_URL}/credits/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/credits/cancel",
                metadata={
                    'user_id': str(user.id),
                    'credits': str(pack["credits"]),
                    'type': 'credit_purchase'
                }
            )

            return session.url

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create credit purchase checkout: {e}")
            raise

    def handle_successful_subscription(
        self,
        db: Session,
        session_id: str
    ) -> Optional[User]:
        """
        Handle successful subscription payment from webhook or redirect.
        Updates user subscription status.
        """
        if not self.is_configured():
            return None

        try:
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status != 'paid':
                logger.warning(f"Session {session_id} not paid: {session.payment_status}")
                return None

            # Get user
            user_id = int(session.metadata['user_id'])
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                logger.error(f"User {user_id} not found for session {session_id}")
                return None

            # Update subscription
            tier_str = session.metadata['tier']
            tier = SubscriptionTier(tier_str)
            billing_period = session.metadata.get('billing_period', 'monthly')

            user.subscription_tier = tier
            user.stripe_subscription_id = session.subscription

            # Set expiration date
            if billing_period == 'monthly':
                user.subscription_valid_until = datetime.utcnow() + timedelta(days=30)
            else:
                user.subscription_valid_until = datetime.utcnow() + timedelta(days=365)

            # Reset credits based on tier
            user.credits_remaining = self.TIER_CREDITS.get(tier, 5)

            db.commit()
            db.refresh(user)

            logger.info(f"User {user_id} upgraded to {tier.value}")
            return user

        except Exception as e:
            logger.error(f"Failed to handle subscription: {e}")
            db.rollback()
            return None

    def handle_successful_credit_purchase(
        self,
        db: Session,
        session_id: str
    ) -> Optional[User]:
        """
        Handle successful credit purchase from webhook or redirect.
        Adds credits to user account.
        """
        if not self.is_configured():
            return None

        try:
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status != 'paid':
                logger.warning(f"Session {session_id} not paid: {session.payment_status}")
                return None

            # Get user
            user_id = int(session.metadata['user_id'])
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                logger.error(f"User {user_id} not found for session {session_id}")
                return None

            # Add credits
            credits = int(session.metadata['credits'])
            user.add_credits(credits)

            db.commit()
            db.refresh(user)

            logger.info(f"User {user_id} purchased {credits} credits")
            return user

        except Exception as e:
            logger.error(f"Failed to handle credit purchase: {e}")
            db.rollback()
            return None

    def cancel_subscription(self, db: Session, user: User) -> bool:
        """
        Cancel user's active subscription.
        Downgrades to FREE tier immediately.
        """
        if not self.is_configured():
            raise ValueError("Stripe is not configured")

        if not user.stripe_subscription_id:
            logger.warning(f"User {user.id} has no subscription to cancel")
            return False

        try:
            # Cancel at period end (user keeps access until expiration)
            stripe.Subscription.modify(
                user.stripe_subscription_id,
                cancel_at_period_end=True
            )

            logger.info(f"Subscription {user.stripe_subscription_id} set to cancel at period end")
            return True

        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {e}")
            raise

    def cancel_subscription_immediately(self, db: Session, user: User) -> bool:
        """
        Immediately cancel user's subscription and downgrade.
        """
        if not self.is_configured():
            raise ValueError("Stripe is not configured")

        if not user.stripe_subscription_id:
            return False

        try:
            stripe.Subscription.delete(user.stripe_subscription_id)

            # Downgrade to free tier
            user.subscription_tier = SubscriptionTier.FREE
            user.subscription_valid_until = None
            user.stripe_subscription_id = None
            user.credits_remaining = 1

            db.commit()

            logger.info(f"User {user.id} subscription cancelled immediately")
            return True

        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription immediately: {e}")
            raise

    def handle_webhook_event(self, db: Session, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Process Stripe webhook events.
        Returns event processing result.
        """
        if not self.is_configured() or not self.webhook_secret:
            raise ValueError("Stripe webhook not configured")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise

        # Handle different event types
        event_type = event['type']
        data = event['data']['object']

        result = {"event_type": event_type, "processed": False}

        if event_type == 'checkout.session.completed':
            session_type = data.get('metadata', {}).get('type')

            if session_type == 'subscription':
                user = self.handle_successful_subscription(db, data['id'])
                result["processed"] = user is not None
            elif session_type == 'credit_purchase':
                user = self.handle_successful_credit_purchase(db, data['id'])
                result["processed"] = user is not None

        elif event_type == 'customer.subscription.deleted':
            # Subscription cancelled or expired
            subscription_id = data['id']
            user = db.query(User).filter(
                User.stripe_subscription_id == subscription_id
            ).first()

            if user:
                user.subscription_tier = SubscriptionTier.FREE
                user.subscription_valid_until = None
                user.stripe_subscription_id = None
                user.credits_remaining = 1
                db.commit()
                result["processed"] = True
                logger.info(f"User {user.id} subscription expired/cancelled")

        elif event_type == 'invoice.payment_failed':
            # Payment failed - notify user
            customer_id = data.get('customer')
            user = db.query(User).filter(
                User.stripe_customer_id == customer_id
            ).first()

            if user:
                # TODO: Send notification to user about failed payment
                logger.warning(f"Payment failed for user {user.id}")
                result["processed"] = True

        elif event_type == 'customer.subscription.updated':
            # Subscription updated (plan change, renewal, etc.)
            subscription_id = data['id']
            user = db.query(User).filter(
                User.stripe_subscription_id == subscription_id
            ).first()

            if user:
                # Update subscription end date
                current_period_end = data.get('current_period_end')
                if current_period_end:
                    user.subscription_valid_until = datetime.fromtimestamp(current_period_end)
                    db.commit()
                result["processed"] = True

        return result

    def get_subscription_status(self, user: User) -> Optional[Dict[str, Any]]:
        """
        Get detailed subscription status from Stripe.
        """
        if not self.is_configured() or not user.stripe_subscription_id:
            return None

        try:
            subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)

            return {
                "status": subscription.status,
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "canceled_at": datetime.fromtimestamp(subscription.canceled_at) if subscription.canceled_at else None,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Failed to get subscription status: {e}")
            return None

    def _get_tier_description(self, tier: SubscriptionTier) -> str:
        """Get description for subscription tier"""
        descriptions = {
            SubscriptionTier.PRO: "5 books/month, 150k words, series support, cover generation",
            SubscriptionTier.PREMIUM: "Unlimited books, 200k words, priority generation, all features",
        }
        return descriptions.get(tier, "")

    def get_pricing_info(self) -> Dict[str, Any]:
        """Get all pricing information for display"""
        return {
            "subscriptions": {
                tier.value: {
                    "monthly": price["monthly"],
                    "yearly": price["yearly"],
                    "yearly_monthly_equivalent": round(price["yearly"] / 12, 2),
                    "yearly_savings": round((price["monthly"] * 12 - price["yearly"]), 2),
                }
                for tier, price in self.SUBSCRIPTION_PRICES.items()
            },
            "credits": {
                str(size): {
                    "credits": pack["credits"],
                    "price": pack["price"],
                    "price_per_credit": round(pack["price"] / pack["credits"], 2),
                    "savings_percent": pack["discount"],
                }
                for size, pack in self.CREDIT_PACKS.items()
            }
        }


# Singleton instance
stripe_service = StripeService()
