"""Render per-column trend results as a formatted table row."""
from __future__ import annotations

from typing import List, Sequence

from csvlens.column_trend_engine import ColumnTrendEngine

_ANSI_UP   = "\033[32m"   # green
_ANSI_DOWN = "\033[31m"   # red
_ANSI_FLAT = "\033[33m"   # yellow
_ANSI_RST  = "\033[0m"


class ColumnTrendRenderer:
    """Render trend summaries for visible columns."""

    def __init__(self, engine: ColumnTrendEngine, col_width: int = 18) -> None:
        if col_width < 6:
            raise ValueError("col_width must be at least 6")
        self._engine = engine
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _fit(self, text: str) -> str:
        if len(text) > self._col_width:
            return text[: self._col_width - 1] + "…"
        return text.ljust(self._col_width)

    def _colour(self, direction: str, text: str) -> str:
        code = {"up": _ANSI_UP, "down": _ANSI_DOWN, "flat": _ANSI_FLAT}.get(direction, "")
        return f"{code}{text}{_ANSI_RST}" if code else text

    def render_header(self, columns: Sequence[str]) -> str:
        cells = [self._fit(c) for c in columns]
        return " | ".join(cells)

    def render(self, columns: Sequence[str]) -> str:
        """Return a single line showing the trend for each column."""
        cells: List[str] = []
        for col in columns:
            result = self._engine.get(col)
            arrow = {"up": "↑", "down": "↓", "flat": "→"}[result.direction]
            label = f"{arrow} {result.slope:+.3f}"
            coloured = self._colour(result.direction, self._fit(label))
            cells.append(coloured)
        return " | ".join(cells)
