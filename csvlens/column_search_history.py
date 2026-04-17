"""Tracks per-column and global search history for the interactive viewer."""
from __future__ import annotations
from collections import deque
from typing import Deque, Dict, List, Optional

_MAX_HISTORY = 50


class ColumnSearchHistory:
    """Stores recent search patterns globally and per-column."""

    def __init__(self, headers: List[str], max_history: int = _MAX_HISTORY) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        if max_history < 1:
            raise ValueError("max_history must be at least 1")
        self._headers: List[str] = list(headers)
        self._max: int = max_history
        self._global: Deque[str] = deque(maxlen=max_history)
        self._per_column: Dict[str, Deque[str]] = {
            h: deque(maxlen=max_history) for h in self._headers
        }

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def max_history(self) -> int:
        return self._max

    def push_global(self, pattern: str) -> None:
        """Record a global search pattern."""
        if not pattern:
            raise ValueError("pattern must not be empty")
        if not self._global or self._global[-1] != pattern:
            self._global.append(pattern)

    def push_column(self, column: str, pattern: str) -> None:
        """Record a search pattern for a specific column."""
        if column not in self._per_column:
            raise KeyError(f"unknown column: {column!r}")
        if not pattern:
            raise ValueError("pattern must not be empty")
        q = self._per_column[column]
        if not q or q[-1] != pattern:
            q.append(pattern)

    def global_history(self) -> List[str]:
        """Return global history newest-first."""
        return list(reversed(self._global))

    def column_history(self, column: str) -> List[str]:
        """Return per-column history newest-first."""
        if column not in self._per_column:
            raise KeyError(f"unknown column: {column!r}")
        return list(reversed(self._per_column[column]))

    def clear_global(self) -> None:
        self._global.clear()

    def clear_column(self, column: str) -> None:
        if column not in self._per_column:
            raise KeyError(f"unknown column: {column!r}")
        self._per_column[column].clear()

    def clear_all(self) -> None:
        self._global.clear()
        for q in self._per_column.values():
            q.clear()
