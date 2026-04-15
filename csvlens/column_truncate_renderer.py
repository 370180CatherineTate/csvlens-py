"""Renderer that displays truncated column values in a fixed-width table row."""

from __future__ import annotations

from csvlens.column_truncate_engine import ColumnTruncateEngine


class ColumnTruncateRenderer:
    """Renders rows using truncated values from a ColumnTruncateEngine."""

    _MIN_COL_WIDTH = 4

    def __init__(self, engine: ColumnTruncateEngine, col_width: int = 18) -> None:
        if col_width < self._MIN_COL_WIDTH:
            raise ValueError(
                f"col_width must be >= {self._MIN_COL_WIDTH}, got {col_width}"
            )
        self._engine = engine
        self._col_width = col_width

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def col_width(self) -> int:
        return self._col_width

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _fit(self, text: str) -> str:
        """Pad or hard-truncate text to exactly col_width characters."""
        if len(text) > self._col_width:
            return text[: self._col_width - 1] + ">"
        return text.ljust(self._col_width)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render_header(self) -> str:
        """Return a formatted header line."""
        cells = [self._fit(h) for h in self._engine.headers]
        return " | ".join(cells)

    def render_row(self, row: dict[str, str]) -> str:
        """Return a formatted data row with truncated values."""
        truncated = self._engine.truncate_row(row)
        cells = [self._fit(truncated.get(h, "")) for h in self._engine.headers]
        return " | ".join(cells)

    def render_all(self, rows: list[dict[str, str]]) -> str:
        """Render header + all rows joined by newlines."""
        lines = [self.render_header()]
        lines.extend(self.render_row(r) for r in rows)
        return "\n".join(lines)
