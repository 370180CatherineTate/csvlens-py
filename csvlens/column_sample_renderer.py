from __future__ import annotations

from typing import List

from csvlens.column_sample_engine import ColumnSampleEngine


class ColumnSampleRenderer:
    """Renders per-column sample values as a formatted table."""

    def __init__(self, engine: ColumnSampleEngine, col_width: int = 20) -> None:
        if col_width < 4:
            raise ValueError("col_width must be at least 4")
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
        parts = [self._fit(h) for h in self._engine.headers]
        return "  ".join(parts)

    def render_row(self, index: int) -> str:
        """Render sample values at the given index across all columns."""
        parts: List[str] = []
        for col in self._engine.headers:
            result = self._engine.get(col)
            if index < result.count:
                cell = result.values[index]
            else:
                cell = ""
            parts.append(self._fit(cell))
        return "  ".join(parts)

    def render(self) -> str:
        """Render header + all sample rows as a single multi-line string."""
        lines = [self.render_header()]
        sep = "-" * len(lines[0])
        lines.append(sep)
        for i in range(self._engine.sample_size):
            lines.append(self.render_row(i))
        return "\n".join(lines)
