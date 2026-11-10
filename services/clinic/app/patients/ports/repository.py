"""Port of the Patients feature: what the use cases need from storage."""

from typing import Protocol

from app.patients.domain.patient import Patient


class PatientRepository(Protocol):
    """The port: what the use cases need from storage. Two adapters implement it:
    app/patients/adapters/sqlalchemy.py with a table, app/patients/adapters/memory.py with a dictionary."""

    def get(self, patient_id: str) -> Patient | None: ...

    def list(self, offset: int, limit: int, last_name: str | None) -> list[Patient]:
        """At most `limit` patients from `offset`, ordered by last name, first name, id;
        `last_name` is a case-insensitive filter."""
        ...

    def add(self, patient: Patient) -> None: ...

    def update(self, patient: Patient) -> None: ...

    def delete(self, patient_id: str) -> None:
        """Deletes the patient and the patient's appointments."""
        ...
