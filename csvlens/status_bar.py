"""Status bar renderer for the csvlens TUI.

Builds a single-line status string summarising the current viewer state:
row/page position, active filters, sort column, and frozen column count.
"""

from __future__ import annotations

from typing import Optional


class StatusBar:
    """Compose a status-line string from various viewer state fragments."""

    def __init__(
        self,
        *,
        total_rows: int,
        visible_rows: int,
        current_page: int,
        total_pages: int,
        sort_column: Optional[str] = None,
        sort_ascending: bool = True,
        global_filter: Optional[str] = None,
        frozen_count: int = 0,
        search_pattern: Optional[str] = None,
        current_match: int = 0,
        total_matches: int = 0,
    ) -> None:
        if total_rows < 0:
            raise ValueError("total_rows must be >= 0")
        if total_pages < 1:
            raise ValueError("total_pages must be >= 1")
        if current_page < 1 or current_page > total_pages:
            raise ValueError("current_page must be between 1 and total_pages")

        self._total_rows = total_rows
        self._visible_rows = visible_rows
        self._current_page = current_page
        self._total_pages = total_pages
        self._sort_column = sort_column
        self._sort_ascending = sort_ascending
        self._global_filter = global_filter
        self._frozen_count = frozen_count
        self._search_pattern = search_pattern
        self._current_match = current_match
        self._total_matches = total_matches

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self) -> str:
        """Return the full status line as a plain string."""
        parts: list[str] = []

        # Row / page summary
        parts.append(
            f"Rows: {self._visible_rows}/{self._total_rows}  "
            f"Page: {self._current_page}/{self._total_pages}"
        )

        # Sort indicator
        if self._sort_column:
            arrow = "\u25b2" if self._sort_ascending else "\u25bc"
            parts.append(f"Sort: {self._sort_column} {arrow}")

        # Active filter
        if self._global_filter:
            parts.append(f"Filter: {self._global_filter!r}")

        # Frozen columns
        if self._frozen_count:
            parts.append(f"Frozen: {self._frozen_count}")

        # Search match position
        if self._search_pattern:
            if self._total_matches:
                parts.append(
                    f"Search: {self._search_pattern!r} "
                    f"[{self._current_match}/{self._total_matches}]"
                )
            else:
                parts.append(f"Search: {self._search_pattern!r} [no matches]")

        return "  |  ".join(parts)

    def __str__(self) -> str:  # pragma: no cover
        return self.render()
