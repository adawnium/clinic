"""Domain errors: what a use case can refuse. No HTTP here; app/http/problems.py maps them to status codes."""


class DomainError(Exception):
    """Base class of the errors a use case raises on purpose."""


class NotFound(DomainError):
    """The resource does not exist: 'No patient with id p_7f3a1c2e'."""

    def __init__(self, what: str) -> None:
        super().__init__(what)
        self.what = what


class Conflict(DomainError):
    """The current state forbids the operation: an overlapping slot, a patient with upcoming appointments."""

    def __init__(self, why: str) -> None:
        super().__init__(why)
        self.why = why


class InvalidData(DomainError):
    """Well-formed data that breaks a business rule, attached to the offending field of the contract."""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(message)
        self.field = field
        self.message = message
