from __future__ import annotations
from typing import Dict, List, Optional
from csvlens.column_progress_engine import ColumnProgressEngine


class ColumnProgressRenderer:
    """Renders per-column progress bars inside fixed-width cells."""

    FILL = "█"
    EMPTY = "░"

    def __init__(self, engine: ColumnProgressEngine, col_width: int = 16, bar_width: int = 10) -> None:
        if col_width < 4:
            raise ValueError("col_width must be at least 4")
        if bar_width < 2:
            raise ValueError("bar_width must be at least 2")
        self._engine = engine
        self._col_width = col_width
        self._bar_width = bar_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _fit(self, text: str) -> str:
        if len(text) >= self._col_width:
            return text[: self._col_width - 1] + "…"
        return text.ljust(self._col_width)

    def _bar(self, fraction: Optional[float]) -> str:
        if fraction is None:
            return self.EMPTY * self._bar_width
        filled = round(fraction * self._bar_width)
        return self.FILL * filled + self.EMPTY * (self._bar_width - filled)

    def render_header(self) -> str:
        parts = [self._fit(h) for h in self._engine.headers]
        return " | ".join(parts)

    def render_row(self, row: Dict[str, str]) -> str:
        parts = []
        for h in self._engine.headers:
            raw = row.get(h, "")
            frac = self._engine.progress(h, raw)
            bar = self._bar(frac)
            cell = f"{bar} {raw}"
            parts.append(self._fit(cell))
        return " | ".join(parts)

    def render_all(self, rows: List[Dict[str, str]]) -> str:
        lines = [self.render_header()]
        lines.append("-" * len(self.render_header()))
        for row in rows:
            lines.append(self.render_row(row))
        return "\n".join(lines)
