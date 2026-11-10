"""Opaque identifiers, assigned by the server: p_7f3a1c2e for a patient, r_0c21d9ab for an appointment."""

import secrets

PATTERN = r"^[a-z]+_[0-9a-f]{8}$"  # the Identifier schema of the contract


def new_id(prefix: str) -> str:
    """Four random bytes are enough for a clinic; a collision would raise an integrity error."""
    return f"{prefix}_{secrets.token_hex(4)}"
