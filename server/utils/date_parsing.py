import re
from datetime import datetime, timedelta

__all__ = ["is_within_month"]


def is_within_month(s: str) -> str:
    """
    s: "2023-10-31" 같은 문자열
    """

    if not s:
        return False

    try:
        event_date = datetime.strptime(s, "%Y-%m-%d")
        one_month_ago = datetime.now() - timedelta(days=30)
        return event_date >= one_month_ago

    except Exception:
        return False