import logging
from twilio.rest import Client
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def send_order_payment_link(phone: str, order_id: str, payment_link: str):
    """Send payment link to customer via Twilio SMS."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.warning("Twilio credentials missing. SMS not sent.")
        return False

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Thanks for ordering from Meatcraft! Order: {order_id}. Pay here: {payment_link}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone
        )
        logger.info(f"SMS sent to {phone}. SID: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")
        return False
