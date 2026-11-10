"""Unit tests of the Patients use cases and rules, with the in-memory fakes of conftest.py."""

from datetime import date, timedelta

import pytest

from app.patients.domain.patient import Patient, check_birth_date
from app.shared.domain.errors import InvalidData, NotFound
from tests.conftest import NOW


def test_create_assigns_an_identifier_and_stores_the_patient(patient_service, patients_repository):
    patient = patient_service.create(last_name="Martin", first_name="Alice", birth_date=date(1980, 5, 2), phone="+33 6 12 34 56 78")

    assert patient.id.startswith("p_") and len(patient.id) == 10
    assert patients_repository.get(patient.id) == patient
    assert patient.phone == "+33 6 12 34 56 78"


def test_birth_date_today_is_accepted(patient_service):
    patient = patient_service.create(last_name="Martin", first_name="Alice", birth_date=NOW.date())
    assert patient.birth_date == NOW.date()


def test_birth_date_in_the_future_is_rejected(patient_service):
    with pytest.raises(InvalidData) as error:
        patient_service.create(last_name="Martin", first_name="Alice", birth_date=NOW.date() + timedelta(days=1))

    assert error.value.field == "birthDate"
    assert error.value.message == "must be in the past, today included"


def test_check_birth_date_is_the_rule(clock):
    check_birth_date(date(2000, 1, 1), clock.now().date())
    with pytest.raises(InvalidData):
        check_birth_date(date(2099, 1, 1), clock.now().date())


def test_list_pages_with_has_more(patient_service):
    for first_name in ("Alice", "Bob", "Chloe"):
        patient_service.create(last_name="Martin", first_name=first_name, birth_date=date(1980, 5, 2))

    first = patient_service.list_patients(offset=0, limit=2)
    second = patient_service.list_patients(offset=2, limit=2)

    assert [p.first_name for p in first.items] == ["Alice", "Bob"] and first.has_more
    assert [p.first_name for p in second.items] == ["Chloe"] and not second.has_more


def test_list_filters_on_last_name_case_insensitively(patient_service):
    patient_service.create(last_name="Martin", first_name="Alice", birth_date=date(1980, 5, 2))
    patient_service.create(last_name="Dupont", first_name="Bob", birth_date=date(1980, 5, 2))

    page = patient_service.list_patients(offset=0, limit=20, last_name="ma")

    assert [p.last_name for p in page.items] == ["Martin"]


def test_read_returns_the_patient(patient_service, patient):
    assert patient_service.read(patient.id) == patient


def test_read_unknown_patient_is_not_found(patient_service):
    with pytest.raises(NotFound) as error:
        patient_service.read("p_00000000")
    assert error.value.what == "No patient with id p_00000000"


def test_replace_overwrites_every_field(patient_service, patient):
    updated = patient_service.replace(patient.id, last_name="Durand", first_name="Alice", birth_date=date(1981, 6, 3))

    assert updated == Patient(id=patient.id, last_name="Durand", first_name="Alice", birth_date=date(1981, 6, 3), phone=None)
    assert patient_service.read(patient.id) == updated


def test_replace_unknown_patient_is_not_found(patient_service):
    with pytest.raises(NotFound):
        patient_service.replace("p_00000000", last_name="Durand", first_name="Alice", birth_date=date(1981, 6, 3))


def test_replace_checks_the_birth_date(patient_service, patient):
    with pytest.raises(InvalidData):
        patient_service.replace(patient.id, last_name="Durand", first_name="Alice", birth_date=date(2099, 1, 1))


def test_delete_removes_the_patient(patient_service, patient):
    patient_service.delete(patient.id)
    with pytest.raises(NotFound):
        patient_service.read(patient.id)


def test_delete_unknown_patient_is_not_found(patient_service):
    with pytest.raises(NotFound):
        patient_service.delete("p_00000000")


