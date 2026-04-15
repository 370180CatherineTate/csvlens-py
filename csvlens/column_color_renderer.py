"""Renderer that applies column colors to a table row."""
from __future__ import annotations
from typing import Dict, List

from csvlens.column_color_engine import ColumnColorEngine

_MIN_COL_WIDTH = 3


class ColumnColorRenderer:
    """Render a header line and data rows with per-column ANSI colors."""

    def __init__(self, engine: ColumnColorEngine, col_width: int = 14) -> None:
        if col_width < _MIN_COL_WIDTH:
            raise ValueError(f"col_width must be >= {_MIN_COL_WIDTH}")
        self._engine = engine
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _fit(self, text: str) -> str:
        """Truncate or pad *text* to col_width."""
        if len(text) > self._col_width:
            return text[: self._col_width - 1] + "…"
        return text.ljust(self._col_width)

    def render_header(self) -> str:
        """Return a colored header line."""
        parts: List[str] = []
        for h in self._engine.headers:
            cell = self._fit(h)
            parts.append(self._engine.colorize(h, cell))
        return "  ".join(parts)

    def render_row(self, row: Dict[str, str]) -> str:
        """Return a colored data row string."""
        parts: List[str] = []
        for h in self._engine.headers:
            cell = self._fit(row.get(h, ""))
            parts.append(self._engine.colorize(h, cell))
        return "  ".join(parts)

    def render_all(self, rows: List[Dict[str, str]]) -> str:
        """Return header + all rows joined by newlines."""
        lines = [self.render_header()] + [self.render_row(r) for r in rows]
        return "\n".join(lines)
