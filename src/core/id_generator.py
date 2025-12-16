"""
Custom ID Generator for Django models
Avoids UUID, random module, standard Postgres functions, and integer increments
"""

import hashlib
import time

from django.conf import settings


def generate_custom_id(prefix=""):
    """
    Generate a unique identifier based on timestamp and hash
    Format: prefix_timestamp_hash_part
    """
    # Get current timestamp with microseconds for uniqueness
    timestamp = str(time.time())

    # Create a hash of the timestamp combined with Django's secret key for uniqueness
    hash_input = f"{timestamp}{settings.SECRET_KEY}".encode("utf-8")
    hash_obj = hashlib.sha256(hash_input)
    hash_hex = hash_obj.hexdigest()

    # Take a portion of the hash to create the ID
    # Using 12 characters for reasonable length and uniqueness
    hash_part = hash_hex[:12]

    # Combine prefix with timestamp and hash part
    # Use last 10 digits of timestamp to keep it reasonable
    time_part = str(int(float(timestamp) * 1000000))[
        -10:
    ]  # Last 10 digits of microsecond timestamp

    return f"{prefix}{time_part}{hash_part.upper()}"


def generate_task_id():
    """Generate a unique ID for Task objects"""
    return generate_custom_id("TASK_")


def generate_category_id():
    """Generate a unique ID for Category objects"""
    return generate_custom_id("CAT_")
