from datetime import date

from app.patients.domain.patient import Patient, check_birth_date
from app.patients.ports.repository import PatientRepository
from app.appointments.ports.repository import AppointmentRepository
from app.shared.domain.errors import NotFound, Conflict
from app.shared.domain.ids import new_id
from app.shared.domain.page import Page
from app.shared.ports.clock import Clock


class PatientService:
    def __init__(self, repository: PatientRepository, clock: Clock, appointment_repository: AppointmentRepository) -> None:
        self.repository = repository
        self.clock = clock
        self.appointment_repository = appointment_repository

    def list_patients(self, offset: int, limit: int, last_name: str | None = None) -> Page[Patient]:
        rows = self.repository.list(offset, limit + 1, last_name)  # one extra: is there a next page?
        return Page(items=rows[:limit], has_more=len(rows) > limit)

    def create(self, *, last_name: str, first_name: str, birth_date: date, phone: str | None = None) -> Patient:
        check_birth_date(birth_date, self.today())
        patient = Patient(id=new_id("p"), last_name=last_name, first_name=first_name, birth_date=birth_date, phone=phone)
        self.repository.add(patient)
        return patient

    def read(self, patient_id: str) -> Patient:
        patient = self.repository.get(patient_id)
        if patient is None:
            raise NotFound(f"No patient with id {patient_id}")
        return patient

    def replace(self, patient_id: str, *, last_name: str, first_name: str, birth_date: date, phone: str | None = None) -> Patient:
        check_birth_date(birth_date, self.today())
        self.read(patient_id)
        patient = Patient(id=patient_id, last_name=last_name, first_name=first_name, birth_date=birth_date, phone=phone)
        self.repository.update(patient)
        return patient

    def delete(self, patient_id: str) -> None:
        self.read(patient_id)
        
        now = self.clock.now()
        upcoming = self.appointment_repository.list_by_patient(patient_id, limit=1, after=now, cursor=None)
        if upcoming:
            raise Conflict(f"Cannot delete patient {patient_id} because they have upcoming appointments.")
            
        self.repository.delete(patient_id)

    def today(self) -> date:
        return self.clock.now().date()
