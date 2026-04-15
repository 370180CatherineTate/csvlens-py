"""FreezeEngine: manage frozen (pinned) columns in the viewer."""

from __future__ import annotations

from typing import List


class FreezeEngine:
    """Tracks which columns are frozen (pinned to the left).

    Frozen columns always appear first regardless of horizontal scroll
    position.  Only visible columns may be frozen.
    """

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._frozen: List[str] = []

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def headers(self) -> List[str]:
        """All available column headers."""
        return list(self._headers)

    @property
    def frozen(self) -> List[str]:
        """Frozen columns in freeze order."""
        return list(self._frozen)

    @property
    def unfrozen(self) -> List[str]:
        """Columns that are not frozen, preserving original order."""
        return [h for h in self._headers if h not in self._frozen]

    @property
    def frozen_count(self) -> int:
        return len(self._frozen)

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def freeze(self, column: str) -> None:
        """Pin *column* to the left.  No-op if already frozen."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        if column not in self._frozen:
            self._frozen.append(column)

    def unfreeze(self, column: str) -> None:
        """Remove *column* from the frozen set.  No-op if not frozen."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        if column in self._frozen:
            self._frozen.remove(column)

    def unfreeze_all(self) -> None:
        """Clear all frozen columns."""
        self._frozen.clear()

    def toggle(self, column: str) -> bool:
        """Toggle the frozen state of *column*.

        Freezes the column if it is currently unfrozen, or unfreezes it
        if it is currently frozen.

        Returns:
            True if the column is frozen after the call, False otherwise.
        """
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        if column in self._frozen:
            self._frozen.remove(column)
            return False
        self._frozen.append(column)
        return True

    def is_frozen(self, column: str) -> bool:
        """Return True if *column* is currently frozen."""
        return column in self._frozen

    # ------------------------------------------------------------------
    # View helpers
    # ------------------------------------------------------------------

    def ordered_headers(self) -> List[str]:
        """Return headers with frozen columns first, then unfrozen."""
        return self._frozen + self.unfrozen

    def apply(self, row: dict) -> dict:
        """Return a new dict reordered so frozen keys come first."""
        ordered = self.ordered_headers()
        return {k: row[k] for k in ordered if k in row}
