"""
Payment API endpoints
Handles subscription management, credit purchases, and Stripe webhooks
"""

from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.services.stripe_service import stripe_service
from app.models.user import User, SubscriptionTier
from app.api.auth import get_current_active_user


router = APIRouter(prefix="/payments", tags=["Payments"])


# ============== Schemas ==============

class CreateSubscriptionRequest(BaseModel):
    """Request to create subscription checkout"""
    tier: Literal["PRO", "PREMIUM"]
    billing_period: Literal["monthly", "yearly"] = "monthly"


class PurchaseCreditsRequest(BaseModel):
    """Request to purchase credits"""
    pack_size: Literal[1, 5, 10] = 1


class CheckoutResponse(BaseModel):
    """Response with checkout URL"""
    checkout_url: str
    message: str


class SubscriptionStatusResponse(BaseModel):
    """Subscription status response"""
    subscription_tier: str
    is_active: bool
    valid_until: Optional[str]
    credits_remaining: int
    stripe_status: Optional[dict]
    can_cancel: bool


class PricingResponse(BaseModel):
    """Pricing information response"""
    subscriptions: dict
    credits: dict


# ============== Endpoints ==============

@router.get("/pricing", response_model=PricingResponse)
async def get_pricing():
    """
    Get all pricing information for subscriptions and credits.
    Public endpoint - no authentication required.
    """
    return stripe_service.get_pricing_info()


@router.post("/subscribe", response_model=CheckoutResponse)
async def create_subscription_checkout(
    request: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe checkout session for subscription.
    Returns a URL to redirect the user to Stripe checkout.
    """
    if not stripe_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system is not configured"
        )

    # Convert string to enum
    tier = SubscriptionTier[request.tier]

    # Check if user already has this or higher tier
    tier_order = [SubscriptionTier.FREE, SubscriptionTier.PRO, SubscriptionTier.PREMIUM]
    current_tier_index = tier_order.index(current_user.subscription_tier)
    new_tier_index = tier_order.index(tier)

    if new_tier_index <= current_tier_index and current_user.is_subscription_active():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already have {current_user.subscription_tier.value} subscription or higher"
        )

    try:
        checkout_url = stripe_service.create_subscription_checkout(
            db=db,
            user=current_user,
            tier=tier,
            billing_period=request.billing_period
        )

        return CheckoutResponse(
            checkout_url=checkout_url,
            message=f"Redirect to checkout for {tier.value} {request.billing_period} subscription"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )


@router.post("/purchase-credits", response_model=CheckoutResponse)
async def purchase_credits(
    request: PurchaseCreditsRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe checkout session for credit purchase.
    Returns a URL to redirect the user to Stripe checkout.
    """
    if not stripe_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system is not configured"
        )

    try:
        checkout_url = stripe_service.create_credit_purchase_checkout(
            db=db,
            user=current_user,
            pack_size=request.pack_size
        )

        pack_info = stripe_service.CREDIT_PACKS[request.pack_size]

        return CheckoutResponse(
            checkout_url=checkout_url,
            message=f"Redirect to checkout for {pack_info['credits']} credits"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )


@router.get("/subscription-status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's detailed subscription status.
    Includes Stripe subscription details if available.
    """
    stripe_status = None
    if stripe_service.is_configured() and current_user.stripe_subscription_id:
        stripe_status = stripe_service.get_subscription_status(current_user)

    return SubscriptionStatusResponse(
        subscription_tier=current_user.subscription_tier.value,
        is_active=current_user.is_subscription_active(),
        valid_until=current_user.subscription_valid_until.isoformat() if current_user.subscription_valid_until else None,
        credits_remaining=current_user.credits_remaining,
        stripe_status=stripe_status,
        can_cancel=current_user.stripe_subscription_id is not None
    )


@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cancel current subscription at period end.
    User will keep access until the current billing period ends.
    """
    if not stripe_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system is not configured"
        )

    if not current_user.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to cancel"
        )

    try:
        success = stripe_service.cancel_subscription(db, current_user)

        if success:
            return {
                "message": "Subscription will be cancelled at the end of the current billing period",
                "valid_until": current_user.subscription_valid_until.isoformat() if current_user.subscription_valid_until else None
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel subscription"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )


@router.post("/cancel-subscription-immediately")
async def cancel_subscription_immediately(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Immediately cancel subscription and downgrade to FREE tier.
    No refund will be issued.
    """
    if not stripe_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system is not configured"
        )

    if not current_user.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to cancel"
        )

    try:
        success = stripe_service.cancel_subscription_immediately(db, current_user)

        if success:
            return {
                "message": "Subscription cancelled immediately. You have been downgraded to FREE tier.",
                "new_tier": SubscriptionTier.FREE.value,
                "credits_remaining": current_user.credits_remaining
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel subscription"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )


@router.get("/checkout/success")
async def checkout_success(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Handle successful checkout redirect.
    Verifies the session and updates user status.
    """
    if not stripe_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system is not configured"
        )

    try:
        import stripe
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status != 'paid':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment not completed"
            )

        # Verify this session belongs to the current user
        session_user_id = int(session.metadata.get('user_id', 0))
        if session_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This session does not belong to you"
            )

        session_type = session.metadata.get('type')

        if session_type == 'subscription':
            user = stripe_service.handle_successful_subscription(db, session_id)
            if user:
                return {
                    "message": "Subscription activated successfully",
                    "subscription_tier": user.subscription_tier.value,
                    "credits_remaining": user.credits_remaining
                }
        elif session_type == 'credit_purchase':
            user = stripe_service.handle_successful_credit_purchase(db, session_id)
            if user:
                return {
                    "message": "Credits added successfully",
                    "credits_remaining": user.credits_remaining
                }

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to process payment"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify checkout session"
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    This endpoint is called by Stripe when payment events occur.
    """
    if not stripe_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system is not configured"
        )

    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature"
        )

    try:
        result = stripe_service.handle_webhook_event(db, payload, sig_header)

        return {
            "status": "success",
            "event_type": result["event_type"],
            "processed": result["processed"]
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )


@router.get("/credits-info")
async def get_credits_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's credit information and usage statistics.
    """
    return {
        "credits_remaining": current_user.credits_remaining,
        "total_credits_purchased": current_user.total_credits_purchased,
        "books_generated": current_user.books_generated,
        "total_words_generated": current_user.total_words_generated,
        "total_cost_incurred": round(current_user.total_cost_incurred, 2),
        "subscription_tier": current_user.subscription_tier.value,
        "monthly_book_limit": current_user.monthly_book_limit,
    }
