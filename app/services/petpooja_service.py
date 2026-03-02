"""
Petpooja POS service — format and push orders to Petpooja API.
Includes retry logic with exponential backoff (max 3 attempts).
"""
import time
import logging
from typing import Dict, Any, List

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

MAX_RETRIES = 3
BASE_DELAY = 2  # seconds


def _format_order_for_petpooja(
    order: Dict[str, Any],
    items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Format an order into Petpooja-compatible schema.

    Args:
        order: Order data dict.
        items: List of order item dicts.

    Returns:
        Petpooja-formatted order payload.
    """
    petpooja_items = []
    for item in items:
        petpooja_items.append({
            "id": "",  # Petpooja item ID — map via POS catalog if available
            "name": item.get("item_name", ""),
            "quantity": str(item.get("quantity", 1)),
            "price": str(item.get("price", 0)),
            "final_price": str(item.get("final_price", 0)),
            "variation_name": item.get("variation", ""),
            "itemTax": "0",
            "addon": [],
        })

    payload = {
        "app_key": settings.PETPOOJA_APP_KEY,
        "app_secret": settings.PETPOOJA_TOKEN,
        "restID": settings.PETPOOJA_RESTAURANT_ID,
        "orderinfo": {
            "OrderID": order.get("order_id", ""),
            "OnlineOrderID": order.get("order_id", ""),
            "OrderType": "H" if order.get("order_type") == "DELIVERY" else "T",
            "Customer": {
                "name": order.get("customer_name", ""),
                "mobile": order.get("customer_phone", ""),
                "address": order.get("address", ""),
            },
            "PaymentMode": "ONLINE",
            "PaymentStatus": "PAID",
            "TotalAmount": str(order.get("total_amount", 0)),
            "DeliveryCharge": "0",
            "Tax": "0",
            "Discount": "0",
            "items": petpooja_items,
        },
    }

    return payload


async def push_order(
    order: Dict[str, Any],
    items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Push a confirmed order to Petpooja POS with retry logic.

    Args:
        order: Order data dict (order_id, customer_phone, etc.).
        items: List of order item dicts.

    Returns:
        Dict with keys: success, message, attempts

    Raises:
        Exception: If all retry attempts fail.
    """
    payload = _format_order_for_petpooja(order, items)
    url = f"{settings.PETPOOJA_API_URL}/pushOrder"

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("success") in [True, "1", 1]:
                    logger.info(
                        f"Order {order.get('order_id')} pushed to Petpooja "
                        f"successfully on attempt {attempt}"
                    )
                    return {
                        "success": True,
                        "message": "Order pushed to POS successfully",
                        "attempts": attempt,
                    }
                else:
                    error_msg = response_data.get("message", "Unknown POS error")
                    logger.warning(
                        f"Petpooja rejected order {order.get('order_id')} "
                        f"on attempt {attempt}: {error_msg}"
                    )
                    last_error = error_msg
            else:
                last_error = f"HTTP {response.status_code}: {response.text}"
                logger.warning(
                    f"Petpooja API error for order {order.get('order_id')} "
                    f"on attempt {attempt}: {last_error}"
                )

        except httpx.TimeoutException:
            last_error = "Request timeout"
            logger.warning(
                f"Petpooja timeout for order {order.get('order_id')} "
                f"on attempt {attempt}"
            )
        except httpx.ConnectError:
            last_error = "Connection failed"
            logger.warning(
                f"Petpooja connection error for order {order.get('order_id')} "
                f"on attempt {attempt}"
            )
        except Exception as e:
            last_error = str(e)
            logger.error(
                f"Unexpected error pushing order {order.get('order_id')} "
                f"to Petpooja on attempt {attempt}: {e}"
            )

        # Exponential backoff before retry
        if attempt < MAX_RETRIES:
            delay = BASE_DELAY * (2 ** (attempt - 1))
            logger.info(f"Retrying in {delay}s...")
            time.sleep(delay)

    # All attempts failed
    logger.error(
        f"Failed to push order {order.get('order_id')} to Petpooja "
        f"after {MAX_RETRIES} attempts. Last error: {last_error}"
    )
    return {
        "success": False,
        "message": f"POS push failed after {MAX_RETRIES} attempts: {last_error}",
        "attempts": MAX_RETRIES,
    }
