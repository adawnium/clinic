"""SQLAlchemy adapter for the AppointmentRepository port."""

from datetime import datetime
from typing import Sequence

from sqlalchemy import DateTime, ForeignKey, Integer, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.appointments.domain.appointment import Appointment
from app.appointments.ports.repository import AppointmentRepository
from app.shared.adapters.db import Base


class AppointmentRow(Base):
    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    patient_id: Mapped[str] = mapped_column(String, ForeignKey("patients.id"))
    start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str | None] = mapped_column(String, nullable=True)

    def to_domain(self) -> Appointment:
        return Appointment(
            id=self.id,
            patient_id=self.patient_id,
            start=self.start,
            duration_minutes=self.duration_minutes,
            reason=self.reason,
        )


class SqlAlchemyAppointmentRepository(AppointmentRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, appointment_id: str) -> Appointment | None:
        row = self.session.get(AppointmentRow, appointment_id)
        return row.to_domain() if row else None

    def list_by_patient(self, patient_id: str, limit: int, after: datetime | None, cursor: str | None) -> list[Appointment]:
        stmt = select(AppointmentRow).where(AppointmentRow.patient_id == patient_id).order_by(AppointmentRow.start)
        if after:
            stmt = stmt.where(AppointmentRow.start > after)
        # Gestion simplifiée du curseur pour l'exemple
        if cursor:
            stmt = stmt.where(AppointmentRow.id > cursor)
            
        rows: Sequence[AppointmentRow] = self.session.execute(stmt.limit(limit)).scalars().all()
        return [row.to_domain() for row in rows]

    def find_overlap(self, start: datetime, end: datetime) -> Appointment | None:
        # SQLite gère mal l'addition de temps en SQL. 
        # On récupère les RDV autour de cette date, et on filtre en Python (le cabinet n'a qu'un praticien, le volume journalier est faible).
        start_of_day = start.replace(hour=0, minute=0, second=0)
        stmt = select(AppointmentRow).where(AppointmentRow.start >= start_of_day)
        rows: Sequence[AppointmentRow] = self.session.execute(stmt).scalars().all()
        
        for row in rows:
            app = row.to_domain()
            if start < app.end and app.start < end:
                return app
        return None

    def add(self, appointment: Appointment) -> None:
        row = AppointmentRow(
            id=appointment.id,
            patient_id=appointment.patient_id,
            start=appointment.start,
            duration_minutes=appointment.duration_minutes,
            reason=appointment.reason,
        )
        self.session.add(row)

    def delete(self, appointment_id: str) -> None:
        row = self.session.get(AppointmentRow, appointment_id)
        if row:
            self.session.delete(row)