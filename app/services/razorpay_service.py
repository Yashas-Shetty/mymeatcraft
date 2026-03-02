"""
Razorpay payment service — create payment links and verify signatures.
"""
import logging
from typing import Dict, Any

import razorpay

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize Razorpay client
_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_payment_link(
    order_id: str,
    amount: float,
    customer_phone: str,
    customer_name: str,
    description: str = "Meatcraft Order Payment",
) -> Dict[str, Any]:
    """
    Create a Razorpay payment link for the given order.

    Args:
        order_id: Unique order ID (e.g., MC-1234AB).
        amount: Total amount in INR (will be converted to paise).
        customer_phone: Customer phone number.
        customer_name: Customer name.
        description: Payment description.

    Returns:
        Dict with keys: payment_link_url, payment_link_id
    """
    amount_in_paise = int(amount * 100)

    payload = {
        "amount": amount_in_paise,
        "currency": "INR",
        "description": f"{description} - {order_id}",
        "customer": {
            "name": customer_name,
            "contact": customer_phone,
        },
        "notify": {
            "sms": True,
            "email": False,
        },
        "reminder_enable": True,
        "notes": {
            "order_id": order_id,
        },
        "callback_url": "",  # Can be set to a success page URL
        "callback_method": "get",
    }

    try:
        response = _client.payment_link.create(payload)
        payment_link_url = response.get("short_url", response.get("url", ""))
        payment_link_id = response.get("id", "")

        logger.info(
            f"Payment link created for order {order_id}: "
            f"link_id={payment_link_id}, amount={amount}"
        )

        return {
            "payment_link_url": payment_link_url,
            "payment_link_id": payment_link_id,
        }

    except razorpay.errors.BadRequestError as e:
        logger.error(f"Razorpay BadRequest for order {order_id}: {e}")
        raise ValueError(f"Failed to create payment link: {e}")
    except Exception as e:
        logger.error(f"Razorpay error for order {order_id}: {e}")
        raise


def verify_webhook_signature(
    request_body: str,
    signature: str,
) -> bool:
    """
    Verify Razorpay webhook signature.

    Args:
        request_body: Raw request body as string.
        signature: X-Razorpay-Signature header value.

    Returns:
        True if valid, False otherwise.
    """
    try:
        _client.utility.verify_webhook_signature(
            request_body,
            signature,
            settings.RAZORPAY_WEBHOOK_SECRET,
        )
        logger.info("Razorpay webhook signature verified successfully")
        return True
    except razorpay.errors.SignatureVerificationError:
        logger.warning("Razorpay webhook signature verification FAILED")
        return False
    except Exception as e:
        logger.error(f"Webhook signature verification error: {e}")
        return False
