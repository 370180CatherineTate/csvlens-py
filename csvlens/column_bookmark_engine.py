from __future__ import annotations


class ColumnBookmarkEngine:
    """Track bookmarked (starred) columns by name."""

    def __init__(self, headers: list[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: list[str] = list(headers)
        self._bookmarked: set[str] = set()

    @property
    def headers(self) -> list[str]:
        return list(self._headers)

    @property
    def bookmarked(self) -> list[str]:
        """Return bookmarked columns in original header order."""
        return [h for h in self._headers if h in self._bookmarked]

    @property
    def unbookmarked(self) -> list[str]:
        return [h for h in self._headers if h not in self._bookmarked]

    def add(self, column: str) -> None:
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        self._bookmarked.add(column)

    def remove(self, column: str) -> None:
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        self._bookmarked.discard(column)

    def toggle(self, column: str) -> bool:
        """Toggle bookmark; return True if now bookmarked."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        if column in self._bookmarked:
            self._bookmarked.discard(column)
            return False
        self._bookmarked.add(column)
        return True

    def is_bookmarked(self, column: str) -> bool:
        return column in self._bookmarked

    def clear(self) -> None:
        self._bookmarked.clear()
