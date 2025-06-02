import stripe
from models import User
from fastapi import Depends, HTTPException, status
from core.config import settings
from .auth import get_current_user

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

async def stripe_payment(
    amount: int,  # in cents
    currency: str = "usd",
    user: User = Depends(get_current_user)
) -> stripe.PaymentIntent:
    """Create a Stripe payment intent for the specified amount"""
    try:
        return stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata={"user_id": str(user.id)},
            description=f"Payment from {user.username}",
            automatic_payment_methods={"enabled": True}
        )
    except stripe.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.user_message)
        )