"""
Razorpay webhook signature verification utility.
"""
import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)


def verify_razorpay_signature(
    request_body: bytes,
    signature: str,
    webhook_secret: str,
) -> bool:
    """
    Verify Razorpay webhook signature using HMAC-SHA256.

    Args:
        request_body: Raw request body bytes.
        signature: X-Razorpay-Signature header value.
        webhook_secret: Razorpay webhook secret from config.

    Returns:
        True if signature is valid, False otherwise.
    """
    try:
        expected_signature = hmac.new(
            key=webhook_secret.encode("utf-8"),
            msg=request_body,
            digestmod=hashlib.sha256,
        ).hexdigest()

        is_valid = hmac.compare_digest(expected_signature, signature)

        if not is_valid:
            logger.warning("Razorpay webhook signature mismatch")

        return is_valid

    except Exception as e:
        logger.error(f"Webhook signature verification error: {e}")
        return False
