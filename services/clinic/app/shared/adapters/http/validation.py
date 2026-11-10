"""Strictness rules of the contract, shared by every input model: a string is a string, never null."""


def expect_string(v):
    """The contract says "string": a number in place of a date is an error, not a conversion."""
    if not isinstance(v, str):
        raise ValueError("expected a string")
    return v


def not_null(v):
    """An optional field may be absent; it cannot be null, the contract says "string"."""
    if v is None:
        raise ValueError("absent or a string, not null")
    return v
