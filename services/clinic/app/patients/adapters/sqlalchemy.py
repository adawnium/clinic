"""Outbound adapter of the Patients feature: the table and the SQLAlchemy implementation of the port."""

from datetime import date

from sqlalchemy import String, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from app.patients.domain.patient import Patient
from app.shared.adapters.db import Base
from app.shared.domain.errors import NotFound


class PatientModel(Base):
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    last_name: Mapped[str] = mapped_column(String(100), index=True)
    first_name: Mapped[str] = mapped_column(String(100))
    birth_date: Mapped[date]
    phone: Mapped[str | None] = mapped_column(String(20))


def to_domain(row: PatientModel) -> Patient:
    return Patient(id=row.id, last_name=row.last_name, first_name=row.first_name, birth_date=row.birth_date, phone=row.phone)


class SqlAlchemyPatientRepository:
    """Each method is one unit of work: it opens a session, runs, commits if it wrote, closes."""

    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self.sessions = sessions

    def get(self, patient_id: str) -> Patient | None:
        with self.sessions() as s:
            row = s.get(PatientModel, patient_id)
            return to_domain(row) if row is not None else None

    def list(self, offset: int, limit: int, last_name: str | None) -> list[Patient]:
        query = select(PatientModel).order_by(PatientModel.last_name, PatientModel.first_name, PatientModel.id)
        if last_name:
            query = query.where(func.lower(PatientModel.last_name).contains(last_name.lower()))
        with self.sessions() as s:
            return [to_domain(row) for row in s.scalars(query.offset(offset).limit(limit))]

    def add(self, patient: Patient) -> None:
        with self.sessions.begin() as s:
            s.add(PatientModel(id=patient.id, last_name=patient.last_name, first_name=patient.first_name, birth_date=patient.birth_date, phone=patient.phone))

    def update(self, patient: Patient) -> None:
        with self.sessions.begin() as s:
            row = s.get(PatientModel, patient.id)
            if row is None:
                raise NotFound(f"No patient with id {patient.id}")
            row.last_name, row.first_name = patient.last_name, patient.first_name
            row.birth_date, row.phone = patient.birth_date, patient.phone

    def delete(self, patient_id: str) -> None:
        # The appointments follow: ON DELETE CASCADE on appointments.patient_id (app/appointments/repository.py).
        with self.sessions.begin() as s:
            row = s.get(PatientModel, patient_id)
            if row is not None:
                s.delete(row)
