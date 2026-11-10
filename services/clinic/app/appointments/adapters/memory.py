from datetime import datetime

from app.appointments.domain.appointment import Appointment


class InMemoryAppointmentRepository:
    def __init__(self) -> None:
        self.rows: dict[str, Appointment] = {}

    def get(self, appointment_id: str) -> Appointment | None:
        return self.rows.get(appointment_id)

    def list_by_patient(self, patient_id: str, limit: int, after: datetime | None = None, cursor: str | None = None) -> list[Appointment]:
        rows = [a for a in self.rows.values() if a.patient_id == patient_id]
        if after:
            rows = [a for a in rows if a.start > after]
        # Dans un vrai cas, on gérerait le cursor ici. Pour la mémoire, on trie par date de début.
        rows.sort(key=lambda a: a.start)
        return rows[:limit]

    def find_overlap(self, start: datetime, end: datetime) -> Appointment | None:
        for app in self.rows.values():
            if start < app.end and app.start < end:
                return app
        return None

    def add(self, appointment: Appointment) -> None:
        self.rows[appointment.id] = appointment

    def delete(self, appointment_id: str) -> None:
        self.rows.pop(appointment_id, None)