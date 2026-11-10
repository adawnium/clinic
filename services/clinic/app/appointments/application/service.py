from datetime import datetime, timedelta

from app.appointments.domain.appointment import (
    Appointment,
    check_duration,
    check_reason,
    check_start,
)
from app.appointments.ports.repository import AppointmentRepository
from app.shared.domain.errors import Conflict, NotFound
from app.shared.domain.ids import new_id
from app.shared.domain.page import Page


class AppointmentService:
    def __init__(self, repository: AppointmentRepository) -> None:
        self.repository = repository

    def list_appointments(self, patient_id: str, limit: int, after: datetime | None = None, cursor: str | None = None) -> Page[Appointment]:
        rows = self.repository.list_by_patient(patient_id, limit + 1, after, cursor)  # one extra: is there a next page?
        return Page(items=rows[:limit], has_more=len(rows) > limit)

    def create(self, *, patient_id: str, start: datetime, duration_minutes: int, reason: str | None = None) -> Appointment:
        check_start(start)
        check_duration(duration_minutes)
        check_reason(reason)

        end = start + timedelta(minutes=duration_minutes)
        overlap = self.repository.find_overlap(start, end)
        if overlap is not None:
            raise Conflict("A slot that overlaps another is refused.")

        appointment = Appointment(
            id=new_id("r"),  # Assigne 'r_' + la suite hexadécimale via l'utilitaire partagé
            patient_id=patient_id,
            start=start,
            duration_minutes=duration_minutes,
            reason=reason,
        )
        self.repository.add(appointment)
        return appointment

    def read(self, appointment_id: str) -> Appointment:
        appointment = self.repository.get(appointment_id)
        if appointment is None:
            raise NotFound(f"No appointment with id {appointment_id}")
        return appointment

    def delete(self, appointment_id: str) -> None:
        self.read(appointment_id)
        self.repository.delete(appointment_id)