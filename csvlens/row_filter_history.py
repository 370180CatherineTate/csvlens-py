"""Tracks the history of applied filters for undo/redo navigation."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FilterSnapshot:
    global_filter: Optional[str] = None
    column_filter: Optional[tuple[str, str]] = None

    def is_empty(self) -> bool:
        return self.global_filter is None and self.column_filter is None

    def description(self) -> str:
        if self.global_filter and self.column_filter:
            col, pat = self.column_filter
            return f"global={self.global_filter!r}, column={col!r}:{pat!r}"
        if self.global_filter:
            return f"global={self.global_filter!r}"
        if self.column_filter:
            col, pat = self.column_filter
            return f"column={col!r}:{pat!r}"
        return "<empty>"


class RowFilterHistory:
    """Maintains an undo/redo stack of FilterSnapshot entries."""

    def __init__(self, max_size: int = 50) -> None:
        if max_size < 1:
            raise ValueError("max_size must be at least 1")
        self._max_size = max_size
        self._stack: list[FilterSnapshot] = []
        self._cursor: int = -1

    @property
    def max_size(self) -> int:
        return self._max_size

    @property
    def current(self) -> Optional[FilterSnapshot]:
        if self._cursor < 0:
            return None
        return self._stack[self._cursor]

    @property
    def can_undo(self) -> bool:
        return self._cursor > 0

    @property
    def can_redo(self) -> bool:
        return self._cursor < len(self._stack) - 1

    def push(self, snapshot: FilterSnapshot) -> None:
        """Record a new filter state, discarding any redo history.

        If the new snapshot is identical to the current one, it is not
        recorded to avoid polluting the history with duplicate entries.
        """
        # Skip duplicate consecutive entries
        if self.current == snapshot:
            return
        # Truncate forward history
        self._stack = self._stack[: self._cursor + 1]
        self._stack.append(snapshot)
        if len(self._stack) > self._max_size:
            self._stack.pop(0)
        self._cursor = len(self._stack) - 1

    def undo(self) -> Optional[FilterSnapshot]:
        """Step back to the previous snapshot and return it."""
        if not self.can_undo:
            return None
        self._cursor -= 1
        return self._stack[self._cursor]

    def redo(self) -> Optional[FilterSnapshot]:
        """Step forward to the next snapshot and return it."""
        if not self.can_redo:
            return None
        self._cursor += 1
        return self._stack[self._cursor]

    def clear(self) -> None:
        self._stack = []
        self._cursor = -1

    def history_descriptions(self) -> list[str]:
        return [s.description() for s in self._stack]
