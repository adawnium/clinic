"""In-memory adapter of the PatientRepository port: a dictionary. The same port as the SQLAlchemy adapter,
without a database: the use cases and their rules are tested against it in a fraction of a second."""

from app.patients.domain.patient import Patient


class InMemoryPatientRepository:
    def __init__(self) -> None:
        self.rows: dict[str, Patient] = {}

    def get(self, patient_id: str) -> Patient | None:
        return self.rows.get(patient_id)

    def list(self, offset: int, limit: int, last_name: str | None) -> list[Patient]:
        rows = sorted(self.rows.values(), key=lambda p: (p.last_name, p.first_name, p.id))
        if last_name:
            rows = [p for p in rows if last_name.lower() in p.last_name.lower()]
        return rows[offset : offset + limit]

    def add(self, patient: Patient) -> None:
        self.rows[patient.id] = patient

    def update(self, patient: Patient) -> None:
        self.rows[patient.id] = patient

    def delete(self, patient_id: str) -> None:
        self.rows.pop(patient_id, None)
