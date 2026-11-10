"""Representations of the Patients feature: the mirror of the contract (contracts/clinic.openapi.yaml).

The input model checks the shape (types, lengths, patterns, unknown fields); the business rules are in
domain/patient.py. The output model adds what the server assigns: the identifier and the links."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.patients.domain import patient as domain
from app.shared.adapters.http.validation import expect_string, not_null
from app.shared.domain.ids import PATTERN


class PatientFields(BaseModel):
    lastName: str = Field(min_length=1, max_length=100, strict=True)
    firstName: str = Field(min_length=1, max_length=100, strict=True)
    birthDate: date = Field(description="In the past, today included")
    phone: str | None = Field(default=None, pattern=r"^\+?[0-9 ]{6,20}$", strict=True)


class PatientCreate(PatientFields):
    model_config = ConfigDict(extra="forbid")  # an unknown field is an error, not a silent oversight

    @field_validator("birthDate", mode="before")
    @classmethod
    def birth_date_as_string(cls, v):
        return expect_string(v)

    @field_validator("phone", mode="before")
    @classmethod
    def phone_not_null(cls, v):
        return not_null(v)


class Links(BaseModel):
    appointments: str


class Patient(PatientFields):
    id: str = Field(pattern=PATTERN)
    links: Links


class PatientPage(BaseModel):
    items: list[Patient]
    nextCursor: str | None = None


def to_representation(p: domain.Patient) -> Patient:
    return Patient(
        id=p.id,
        lastName=p.last_name,
        firstName=p.first_name,
        birthDate=p.birth_date,
        phone=p.phone,
        links=Links(appointments=f"/patients/{p.id}/appointments"),
    )
