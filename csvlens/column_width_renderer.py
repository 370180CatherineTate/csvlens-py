"""Renders a header + data rows using a ColumnWidthProfile."""

from __future__ import annotations

from typing import Dict, List

from csvlens.column_width_profile import ColumnWidthProfile


class ColumnWidthRenderer:
    """Formats rows into fixed-width columns according to a profile."""

    SEPARATOR: str = "  "

    def __init__(self, profile: ColumnWidthProfile) -> None:
        self._profile = profile

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def render_header(self) -> str:
        """Return the header line as a formatted string."""
        parts = [
            self._fit(col, self._profile.width_for(col))
            for col in self._profile.headers
        ]
        return self.SEPARATOR.join(parts)

    def render_row(self, row: Dict[str, str]) -> str:
        """Return a single data row as a formatted string."""
        parts = [
            self._fit(row.get(col, "") or "", self._profile.width_for(col))
            for col in self._profile.headers
        ]
        return self.SEPARATOR.join(parts)

    def render_all(self, rows: List[Dict[str, str]]) -> str:
        """Return header + all rows joined by newlines."""
        lines = [self.render_header()]
        lines.extend(self.render_row(r) for r in rows)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    @staticmethod
    def _fit(text: str, width: int) -> str:
        """Truncate or pad *text* to exactly *width* characters."""
        if len(text) > width:
            return text[: width - 1] + "…"
        return text.ljust(width)
