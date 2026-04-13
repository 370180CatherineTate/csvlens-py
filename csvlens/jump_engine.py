"""JumpEngine: navigate to a specific row or bookmark by index or name."""

from __future__ import annotations

from typing import List, Optional


class JumpEngine:
    """Resolves jump targets within a dataset.

    Supports jumping to:
    - An absolute row index (0-based internally, 1-based in user input).
    - A named bookmark stored as a row index.
    """

    def __init__(self, total_rows: int, bookmarks: Optional[dict] = None) -> None:
        if total_rows < 0:
            raise ValueError("total_rows must be >= 0")
        self._total_rows = total_rows
        # bookmarks: {name: row_index (0-based)}
        self._bookmarks: dict = bookmarks if bookmarks is not None else {}

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def total_rows(self) -> int:
        return self._total_rows

    @property
    def bookmark_names(self) -> List[str]:
        return list(self._bookmarks.keys())

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def jump_to_row(self, user_row: int) -> int:
        """Convert a 1-based user row number to a valid 0-based index.

        Raises ValueError if out of range or dataset is empty.
        """
        if self._total_rows == 0:
            raise ValueError("Dataset is empty; cannot jump to any row.")
        if user_row < 1 or user_row > self._total_rows:
            raise ValueError(
                f"Row {user_row} is out of range (1–{self._total_rows})."
            )
        return user_row - 1

    def jump_to_bookmark(self, name: str) -> int:
        """Return the 0-based row index for the given bookmark name.

        Raises KeyError if the bookmark does not exist.
        """
        if name not in self._bookmarks:
            raise KeyError(f"Bookmark '{name}' not found.")
        return self._bookmarks[name]

    def resolve(self, target: str) -> int:
        """Resolve a string target to a 0-based row index.

        Tries numeric row first, then bookmark lookup.
        Raises ValueError if the target cannot be resolved.
        """
        target = target.strip()
        if target.isdigit():
            return self.jump_to_row(int(target))
        try:
            return self.jump_to_bookmark(target)
        except KeyError:
            raise ValueError(
                f"Cannot resolve jump target '{target}': "
                "not a valid row number or known bookmark."
            )
