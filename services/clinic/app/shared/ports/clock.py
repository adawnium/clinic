"""The clock port: the use cases ask what time it is, they never call datetime.now() themselves."""

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Implemented by app/shared/adapters/clock.py: the system clock in production, a fixed clock in the tests."""

    def now(self) -> datetime: ...
