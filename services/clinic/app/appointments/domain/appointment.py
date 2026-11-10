import re
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.shared.domain.errors import InvalidData


@dataclass
class Appointment:
    id: str
    patient_id: str
    start: datetime
    duration_minutes: int
    reason: str | None = None

    @property
    def end(self) -> datetime:
        """Helper to calculate the end time of the appointment."""
        return self.start + timedelta(minutes=self.duration_minutes)


def check_appointment_id(appointment_id: str) -> None:
    """The ID is opaque, assigned by the server (r_ + 8 hex characters)."""
    if not re.match(r"^r_[0-9a-f]{8}$", appointment_id):
        raise InvalidData("id", "must start with 'r_' followed by 8 hex characters")


def check_start(start: datetime) -> None:
    """The appointment must have a time zone and a year between 1900 and 2100."""
    if start.tzinfo is None or start.tzinfo.utcoffset(start) is None:
        raise InvalidData("start", "must include a time zone")
    if not (1900 <= start.year <= 2100):
        raise InvalidData("start", "year must be between 1900 and 2100")


def check_duration(duration_minutes: int) -> None:
    """The duration must be between 5 and 240 minutes."""
    if not (5 <= duration_minutes <= 240):
        raise InvalidData("durationMinutes", "must be between 5 and 240")


def check_reason(reason: str | None) -> None:
    """The reason is optional, 200 characters at most."""
    if reason is not None and len(reason) > 200:
        raise InvalidData("reason", "must be 200 characters at most")