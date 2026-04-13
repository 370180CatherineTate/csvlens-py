"""ColumnResizeRenderer: render a single header/data row using ColumnResizer widths."""

from __future__ import annotations

from csvlens.column_resizer import ColumnResizer

_SEPARATOR = " | "
_TRUNCATION_MARK = "…"


class ColumnResizeRenderer:
    """Renders rows as fixed-width columns according to a ColumnResizer."""

    def __init__(self, resizer: ColumnResizer, separator: str = _SEPARATOR) -> None:
        if not isinstance(resizer, ColumnResizer):
            raise TypeError("resizer must be a ColumnResizer instance")
        self._resizer = resizer
        self._sep = separator

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fit(self, text: str, width: int) -> str:
        """Pad or truncate *text* to exactly *width* characters."""
        if len(text) > width:
            if width <= 1:
                return text[:width]
            return text[: width - 1] + _TRUNCATION_MARK
        return text.ljust(width)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render_header(self, visible_columns: list[str] | None = None) -> str:
        """Return a formatted header row string."""
        cols = visible_columns if visible_columns is not None else self._resizer.headers
        cells = [self._fit(c, self._resizer.get_width(c)) for c in cols]
        return self._sep.join(cells)

    def render_row(
        self,
        row: dict[str, str],
        visible_columns: list[str] | None = None,
    ) -> str:
        """Return a formatted data row string."""
        cols = visible_columns if visible_columns is not None else self._resizer.headers
        cells = [self._fit(row.get(c, ""), self._resizer.get_width(c)) for c in cols]
        return self._sep.join(cells)

    def render_divider(self, visible_columns: list[str] | None = None) -> str:
        """Return a divider line matching the header width."""
        cols = visible_columns if visible_columns is not None else self._resizer.headers
        cells = ["-" * self._resizer.get_width(c) for c in cols]
        return self._sep.join(cells)

    def render_table(
        self,
        rows: list[dict[str, str]],
        visible_columns: list[str] | None = None,
        include_header: bool = True,
    ) -> str:
        """Render a full table (header + divider + data rows) as a string."""
        lines: list[str] = []
        if include_header:
            lines.append(self.render_header(visible_columns))
            lines.append(self.render_divider(visible_columns))
        for row in rows:
            lines.append(self.render_row(row, visible_columns))
        return "\n".join(lines)
