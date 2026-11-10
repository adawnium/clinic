"""Domain of the Patients feature: the entity and its business rules. No framework here."""

from dataclasses import dataclass
from datetime import date

from app.shared.domain.errors import InvalidData


@dataclass
class Patient:
    id: str
    last_name: str
    first_name: str
    birth_date: date
    phone: str | None = None


def check_birth_date(birth_date: date, today: date) -> None:
    """A patient was born: the birth date is in the past, today included."""
    if birth_date > today:
        raise InvalidData("birthDate", "must be in the past, today included")

