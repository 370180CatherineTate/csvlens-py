"""Engine for toggling word-wrap on individual columns."""
from __future__ import annotations

from typing import List, Dict


class ColumnWrapEngine:
    """Tracks which columns have word-wrap enabled and wraps cell text.

    Args:
        headers: Non-empty list of column header names.
        wrap_width: Maximum character width before wrapping. Must be >= 4.

    Raises:
        ValueError: If headers is empty or wrap_width is too small.
    """

    def __init__(self, headers: List[str], wrap_width: int = 20) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        if wrap_width < 4:
            raise ValueError("wrap_width must be >= 4")
        self._headers: List[str] = list(headers)
        self._wrap_width = wrap_width
        self._wrapped: Dict[str, bool] = {h: False for h in self._headers}

    @property
    def headers(self) -> List[str]:
        """Return a copy of the header list."""
        return list(self._headers)

    @property
    def wrap_width(self) -> int:
        """Current wrap width."""
        return self._wrap_width

    @property
    def wrapped_columns(self) -> List[str]:
        """Return list of columns that have wrap enabled."""
        return [h for h in self._headers if self._wrapped[h]]

    def is_wrapped(self, column: str) -> bool:
        """Return True if *column* has wrap enabled."""
        if column not in self._wrapped:
            raise KeyError(f"Unknown column: {column!r}")
        return self._wrapped[column]

    def enable(self, column: str) -> None:
        """Enable word-wrap for *column*."""
        if column not in self._wrapped:
            raise KeyError(f"Unknown column: {column!r}")
        self._wrapped[column] = True

    def disable(self, column: str) -> None:
        """Disable word-wrap for *column*."""
        if column not in self._wrapped:
            raise KeyError(f"Unknown column: {column!r}")
        self._wrapped[column] = False

    def toggle(self, column: str) -> bool:
        """Toggle wrap for *column* and return the new state."""
        if column not in self._wrapped:
            raise KeyError(f"Unknown column: {column!r}")
        self._wrapped[column] = not self._wrapped[column]
        return self._wrapped[column]

    def wrap_cell(self, column: str, text: str) -> List[str]:
        """Return *text* split into lines according to wrap rules.

        If wrap is disabled for *column* the original text is returned as a
        single-element list.  Otherwise the text is broken on spaces where
        possible, falling back to hard-wrapping at *wrap_width* characters.
        """
        if column not in self._wrapped:
            raise KeyError(f"Unknown column: {column!r}")
        if not self._wrapped[column] or len(text) <= self._wrap_width:
            return [text]
        lines: List[str] = []
        words = text.split(" ")
        current = ""
        for word in words:
            if not current:
                current = word
            elif len(current) + 1 + len(word) <= self._wrap_width:
                current += " " + word
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        # Hard-wrap any line still exceeding wrap_width
        result: List[str] = []
        for line in lines:
            while len(line) > self._wrap_width:
                result.append(line[: self._wrap_width])
                line = line[self._wrap_width :]
            result.append(line)
        return result
