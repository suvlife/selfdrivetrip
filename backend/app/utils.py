"""Shared utility functions."""

import uuid
import random
import string
from datetime import datetime
from typing import Optional


def generate_share_id(length: int = 8) -> str:
    """Generate a short, URL-safe share ID."""
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choices(chars, k=length))


def generate_uuid() -> str:
    """Generate a UUID4 string."""
    return str(uuid.uuid4())


def parse_float(value: any, default: float = 0.0) -> float:
    """Safely parse a float from various inputs."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def parse_int(value: any, default: int = 0) -> int:
    """Safely parse an int from various inputs."""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
