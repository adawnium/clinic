"""Unit tests of the Appointments use cases and rules, with the in-memory fakes of conftest.py."""

from datetime import datetime, timezone, timedelta
import pytest

from app.appointments.domain.appointment import (
    Appointment, 
    check_start, 
    check_duration, 
    check_reason, 
    check_appointment_id
)
from app.shared.domain.errors import InvalidData, NotFound, Conflict
from tests.conftest import NOW


def test_create_assigns_an_identifier_and_stores_the_appointment(appointment_service, appointments_repository, patient):
    start = NOW + timedelta(days=1)
    appointment = appointment_service.create(
        patient_id=patient.id,
        start=start,
        duration_minutes=30,
        reason="Checkup"
    )

    assert appointment.id.startswith("r_") and len(appointment.id) == 10
    assert appointments_repository.get(appointment.id) == appointment
    assert appointment.patient_id == patient.id
    assert appointment.duration_minutes == 30
    assert appointment.reason == "Checkup"


def test_appointment_slot_overlap_is_rejected(appointment_service, patient):
    start = NOW + timedelta(days=1)
    appointment_service.create(patient_id=patient.id, start=start, duration_minutes=60)

    with pytest.raises(Conflict):
        appointment_service.create(patient_id=patient.id, start=start + timedelta(minutes=30), duration_minutes=30)


def test_past_appointment_is_accepted(appointment_service, patient):
    past_start = datetime(2020, 1, 1, 10, 0, tzinfo=timezone.utc)
    appointment = appointment_service.create(
        patient_id=patient.id,
        start=past_start,
        duration_minutes=30,
        reason="Past visit"
    )
    assert appointment.id.startswith("r_")


def test_appointment_duration_out_of_bounds_is_rejected(appointment_service, patient):
    start = NOW + timedelta(days=1)
    
    with pytest.raises(InvalidData) as error:
        appointment_service.create(patient_id=patient.id, start=start, duration_minutes=4)
    assert error.value.field == "durationMinutes"

    with pytest.raises(InvalidData) as error:
        appointment_service.create(patient_id=patient.id, start=start, duration_minutes=241)
    assert error.value.field == "durationMinutes"


def test_appointment_year_out_of_bounds_is_rejected(appointment_service, patient):
    with pytest.raises(InvalidData):
        appointment_service.create(patient_id=patient.id, start=datetime(1899, 12, 31, 10, 0, tzinfo=timezone.utc), duration_minutes=30)

    with pytest.raises(InvalidData):
        appointment_service.create(patient_id=patient.id, start=datetime(2101, 1, 1, 10, 0, tzinfo=timezone.utc), duration_minutes=30)


def test_appointment_without_timezone_is_rejected(appointment_service, patient):
    with pytest.raises(InvalidData):
        appointment_service.create(patient_id=patient.id, start=datetime(2026, 6, 1, 10, 0), duration_minutes=30)


def test_appointment_reason_too_long_is_rejected(appointment_service, patient):
    start = NOW + timedelta(days=1)
    long_reason = "a" * 201
    with pytest.raises(InvalidData) as error:
        appointment_service.create(patient_id=patient.id, start=start, duration_minutes=30, reason=long_reason)
    assert error.value.field == "reason"


def test_read_returns_the_appointment(appointment_service, appointment):
    assert appointment_service.read(appointment.id) == appointment


def test_read_unknown_appointment_is_not_found(appointment_service):
    with pytest.raises(NotFound) as error:
        appointment_service.read("r_00000000")
    assert error.value.what == "No appointment with id r_00000000"


def test_delete_removes_the_appointment(appointment_service, appointments_repository, appointment):
    appointment_service.delete(appointment.id)
    with pytest.raises(NotFound):
        appointment_service.read(appointment.id)


def test_delete_unknown_appointment_is_not_found(appointment_service):
    with pytest.raises(NotFound):
        appointment_service.delete("r_00000000")


def test_delete_patient_with_upcoming_appointments_is_refused(patient_service, appointment_service, patient):
    future_start = NOW + timedelta(days=2)
    appointment_service.create(patient_id=patient.id, start=future_start, duration_minutes=30)

    with pytest.raises(Conflict):
        patient_service.delete(patient.id)


def test_delete_patient_with_past_appointments_is_allowed(patient_service, appointment_service, patient):
    past_start = datetime(2020, 1, 1, 10, 0, tzinfo=timezone.utc)
    appointment_service.create(patient_id=patient.id, start=past_start, duration_minutes=30)

    patient_service.delete(patient.id)
    with pytest.raises(NotFound):
        patient_service.read(patient.id)


def test_list_patient_appointments_sorted_by_start(appointment_service, patient):
    start1 = NOW + timedelta(days=3)
    start2 = NOW + timedelta(days=1)
    start3 = NOW + timedelta(days=2)

    apt1 = appointment_service.create(patient_id=patient.id, start=start1, duration_minutes=30)
    apt2 = appointment_service.create(patient_id=patient.id, start=start2, duration_minutes=30)
    apt3 = appointment_service.create(patient_id=patient.id, start=start3, duration_minutes=30)

    page = appointment_service.list_appointments(patient_id=patient.id, limit=10)
    
    assert [a.id for a in page.items] == [apt2.id, apt3.id, apt1.id]