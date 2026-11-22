from datetime import UTC, datetime


def now_utc() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(UTC)
