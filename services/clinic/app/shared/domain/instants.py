"""Reasoning about instants: everything is in UTC inside the service."""

from datetime import datetime, timezone


def to_utc(d: datetime) -> datetime:
    """SQLite does not keep the time zone: a value read back without one is UTC."""
    return d.astimezone(timezone.utc) if d.tzinfo else d.replace(tzinfo=timezone.utc)


YEAR_MIN, YEAR_MAX = 1900, 2100


def in_range(d: datetime) -> bool:
    """Python's datetime arithmetic overflows at the edges of its range (year 1 or 9999): an instant
    outside a sane window is invalid data, not a server error."""
    return YEAR_MIN <= d.year <= YEAR_MAX
