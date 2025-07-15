# ------------------------------- Utility helpers --------------------------------
from typing import List, Dict, Optional

def safe_get(info: Dict, key: str):
    """Return info[key] or None if missing or falsy."""
    value = info.get(key)
    return value if value not in (None, "", 0) else None


def fmt_money(value: float) -> str:
    """Format a large money number with commas and 0 decimals."""
    return f"${value:,.0f}"


def fmt_price(value: float) -> str:
    return f"${value:,.2f}"