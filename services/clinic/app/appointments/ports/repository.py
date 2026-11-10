from datetime import datetime
from typing import Protocol

from app.appointments.domain.appointment import Appointment


class AppointmentRepository(Protocol):
    """The port: what the use cases need from storage. Two adapters implement it:
    app/appointments/adapters/sqlalchemy.py with a table, app/appointments/adapters/memory.py with a dictionary."""

    def get(self, appointment_id: str) -> Appointment | None: ...

    def list_by_patient(self, patient_id: str, limit: int, after: datetime | None, cursor: str | None) -> list[Appointment]:
        """At most `limit` appointments for a patient, ordered by start time."""
        ...

    def find_overlap(self, start: datetime, end: datetime) -> Appointment | None:
        """Returns an existing appointment that overlaps with the given time range, if any."""
        ...

    def add(self, appointment: Appointment) -> None: ...

    def delete(self, appointment_id: str) -> None: ...