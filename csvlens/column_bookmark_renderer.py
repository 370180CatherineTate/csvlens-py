from __future__ import annotations

from csvlens.column_bookmark_engine import ColumnBookmarkEngine

_STAR = "\u2605"
_EMPTY = "\u2606"


class ColumnBookmarkRenderer:
    """Render a header row with bookmark indicators."""

    def __init__(self, engine: ColumnBookmarkEngine, col_width: int = 12) -> None:
        if col_width < 3:
            raise ValueError("col_width must be >= 3")
        self._engine = engine
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _fit(self, text: str) -> str:
        if len(text) > self._col_width:
            return text[: self._col_width - 1] + "…"
        return text.ljust(self._col_width)

    def render_header(self) -> str:
        parts: list[str] = []
        for h in self._engine.headers:
            star = _STAR if self._engine.is_bookmarked(h) else _EMPTY
            parts.append(f"{star} {self._fit(h)}")
        return " | ".join(parts)

    def render_summary(self) -> str:
        """Return a compact summary line listing bookmarked columns."""
        bm = self._engine.bookmarked
        if not bm:
            return "No bookmarked columns."
        return "Bookmarked: " + ", ".join(bm)
