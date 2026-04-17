"""Engine for locking columns so they cannot be hidden, resized, or reordered."""
from __future__ import annotations

from typing import List, Set


class ColumnLockEngine:
    """Track which columns are locked against modification."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._locked: Set[str] = set()

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def locked(self) -> List[str]:
        """Return locked column names in header order."""
        return [h for h in self._headers if h in self._locked]

    @property
    def unlocked(self) -> List[str]:
        """Return unlocked column names in header order."""
        return [h for h in self._headers if h not in self._locked]

    def lock(self, column: str) -> None:
        """Lock a column by name."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        self._locked.add(column)

    def unlock(self, column: str) -> None:
        """Unlock a column by name."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        self._locked.discard(column)

    def is_locked(self, column: str) -> bool:
        """Return True if the column is locked."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        return column in self._locked

    def lock_all(self) -> None:
        """Lock every column."""
        self._locked = set(self._headers)

    def unlock_all(self) -> None:
        """Unlock every column."""
        self._locked.clear()

    def toggle(self, column: str) -> bool:
        """Toggle lock state; returns new locked state."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        if column in self._locked:
            self._locked.discard(column)
            return False
        self._locked.add(column)
        return True
