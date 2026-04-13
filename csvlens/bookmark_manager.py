"""Manages named bookmarks (saved row positions) for quick navigation."""

from __future__ import annotations

from typing import Dict, List, Optional


class BookmarkManager:
    """Store and retrieve named row-index bookmarks within a CSV session."""

    def __init__(self, total_rows: int) -> None:
        if total_rows < 0:
            raise ValueError("total_rows must be non-negative")
        self._total_rows = total_rows
        self._bookmarks: Dict[str, int] = {}

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def total_rows(self) -> int:
        return self._total_rows

    @property
    def names(self) -> List[str]:
        """Return bookmark names in insertion order."""
        return list(self._bookmarks.keys())

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add(self, name: str, row: int) -> None:
        """Add or overwrite a bookmark.

        Parameters
        ----------
        name:
            A non-empty label for the bookmark.
        row:
            Zero-based row index to bookmark.
        """
        if not name or not name.strip():
            raise ValueError("Bookmark name must be a non-empty string")
        if not (0 <= row < self._total_rows):
            raise IndexError(
                f"Row {row} is out of range [0, {self._total_rows - 1}]"
            )
        self._bookmarks[name.strip()] = row

    def remove(self, name: str) -> None:
        """Remove a bookmark by name; raises KeyError if not found."""
        if name not in self._bookmarks:
            raise KeyError(f"Bookmark '{name}' does not exist")
        del self._bookmarks[name]

    def clear(self) -> None:
        """Remove all bookmarks."""
        self._bookmarks.clear()

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, name: str) -> Optional[int]:
        """Return the row index for *name*, or None if not found."""
        return self._bookmarks.get(name)

    def all(self) -> Dict[str, int]:
        """Return a shallow copy of all bookmarks."""
        return dict(self._bookmarks)

    def __len__(self) -> int:
        return len(self._bookmarks)

    def __contains__(self, name: str) -> bool:
        return name in self._bookmarks
