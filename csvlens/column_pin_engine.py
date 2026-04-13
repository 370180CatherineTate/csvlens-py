"""Engine for pinning columns to always appear first in the view."""

from __future__ import annotations

from typing import List


class ColumnPinEngine:
    """Manages a set of pinned columns that are always rendered first."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers = list(headers)
        self._pinned: List[str] = []

    @property
    def headers(self) -> List[str]:
        """Return all column headers in their original order."""
        return list(self._headers)

    @property
    def pinned(self) -> List[str]:
        """Return pinned columns in pin order."""
        return list(self._pinned)

    @property
    def unpinned(self) -> List[str]:
        """Return columns that are not pinned, preserving original order."""
        pinned_set = set(self._pinned)
        return [h for h in self._headers if h not in pinned_set]

    @property
    def ordered(self) -> List[str]:
        """Return all columns with pinned columns first, then unpinned."""
        return self._pinned + self.unpinned

    def pin(self, column: str) -> None:
        """Pin a column. Raises ValueError if column is unknown or already pinned."""
        if column not in self._headers:
            raise ValueError(f"Unknown column: {column!r}")
        if column in self._pinned:
            raise ValueError(f"Column {column!r} is already pinned")
        self._pinned.append(column)

    def unpin(self, column: str) -> None:
        """Unpin a column. Raises ValueError if column is not currently pinned."""
        if column not in self._pinned:
            raise ValueError(f"Column {column!r} is not pinned")
        self._pinned.remove(column)

    def unpin_all(self) -> None:
        """Remove all pinned columns."""
        self._pinned.clear()

    def is_pinned(self, column: str) -> bool:
        """Return True if the column is currently pinned."""
        return column in self._pinned

    def reorder_row(self, row: dict) -> dict:
        """Return a new dict with keys reordered to match ordered columns."""
        return {col: row[col] for col in self.ordered if col in row}
