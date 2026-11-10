"""What a list use case returns: the items of one page and whether a next page exists."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Page[T]:
    items: list[T]
    has_more: bool
