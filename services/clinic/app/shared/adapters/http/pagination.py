"""Opaque cursor pagination: the client computes nothing, it sends back what it was given.

The cursor encodes a position (an offset). The use case returns a Page saying whether a next page
exists; the router turns that into the nextCursor of the response."""

import base64

from fastapi import HTTPException


def decode(cursor: str | None) -> int:
    """The cursor of the request, as an offset; a cursor we did not issue is a malformed request."""
    if cursor is None:
        return 0
    try:
        offset = int(base64.urlsafe_b64decode(cursor.encode()).decode())
        if offset < 0:
            raise ValueError
        return offset
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid cursor")


def encode(offset: int) -> str:
    return base64.urlsafe_b64encode(str(offset).encode()).decode()


def next_cursor(offset: int, limit: int, has_more: bool) -> str | None:
    """The cursor of the next page, or None on the last page."""
    return encode(offset + limit) if has_more else None
