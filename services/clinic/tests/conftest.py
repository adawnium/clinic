import pytest
from datetime import date, datetime, timezone

# Imports partagés
from app.shared.adapters.clock import FixedClock

# Imports Patients
from app.patients.adapters.memory import InMemoryPatientRepository
from app.patients.application.service import PatientService
from app.patients.domain.patient import Patient

# Imports Appointments (à ajouter)
from app.appointments.adapters.memory import InMemoryAppointmentRepository
from app.appointments.application.service import AppointmentService

NOW = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)

@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(NOW)

@pytest.fixture
def patients_repository() -> InMemoryPatientRepository:
    return InMemoryPatientRepository()

# --- NOUVELLES FIXTURES POUR LES RENDEZ-VOUS ---
@pytest.fixture
def appointments_repository() -> InMemoryAppointmentRepository:
    return InMemoryAppointmentRepository()

@pytest.fixture
def appointment_service(appointments_repository: InMemoryAppointmentRepository) -> AppointmentService:
    """Fournit le service des rendez-vous pour les tests de test_appointments_service.py"""
    return AppointmentService(appointments_repository)
# -----------------------------------------------

@pytest.fixture
def patient_service(
    patients_repository: InMemoryPatientRepository, 
    appointments_repository: InMemoryAppointmentRepository, # <-- On ajoute l'argument manquant
    clock: FixedClock
) -> PatientService:
    """Fournit le service des patients avec ses deux dépendances."""
    return PatientService(patients_repository, clock, appointments_repository) # <-- On le passe à l'init

@pytest.fixture
def patient(patients_repository: InMemoryPatientRepository) -> Patient:
    """Génère un patient de test."""
    p = Patient(id="p_123", last_name="Doe", first_name="John", birth_date=date(1990, 1, 1))
    patients_repository.add(p)
    return p

from app.appointments.domain.appointment import Appointment
from datetime import timedelta

@pytest.fixture
def appointment(appointments_repository: InMemoryAppointmentRepository, patient: Patient) -> Appointment:
    """Génère un rendez-vous de test associé au patient de test."""
    app = Appointment(
        id="r_1234abcd",
        patient_id=patient.id,
        start=NOW + timedelta(days=1),  # Demain
        duration_minutes=30,
        reason="Consultation de routine"
    )
    appointments_repository.add(app)
    return app