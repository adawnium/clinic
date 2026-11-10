"""Adapters of the Clock port."""

from datetime import datetime, timezone


class SystemClock:
    """The real clock, used in production (wired in app/main.py)."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class FixedClock:
    """A clock stopped at a chosen instant, for the tests."""

    def __init__(self, at: datetime) -> None:
        self.at = at

    def now(self) -> datetime:
        return self.at
