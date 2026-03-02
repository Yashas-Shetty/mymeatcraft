"""
Utility for generating unique order IDs.
Format: MC-XXXXXX (timestamp-based + random suffix)
"""
import time
import random
import string


def generate_order_id() -> str:
    """
    Generate a unique order ID in the format MC-XXXXXX.
    Uses last 4 digits of timestamp + 2 random uppercase letters.
    """
    timestamp_part = str(int(time.time()))[-4:]
    random_part = "".join(random.choices(string.ascii_uppercase, k=2))
    return f"MC-{timestamp_part}{random_part}"
