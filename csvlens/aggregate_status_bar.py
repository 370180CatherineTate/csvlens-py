"""One-line status bar summarising a chosen column's aggregates."""
from __future__ import annotations

from typing import Optional

from csvlens.column_aggregate_engine import ColumnAggregateEngine


class AggregateStatusBar:
    """Render a compact single-line summary for one column."""

    def __init__(self, engine: ColumnAggregateEngine, width: int = 80) -> None:
        if width < 20:
            raise ValueError("width must be at least 20")
        self._engine = engine
        self._width = width
        self._active: Optional[str] = None

    @property
    def width(self) -> int:
        return self._width

    def set_active_column(self, column: Optional[str]) -> None:
        """Choose which column to display; None clears the bar."""
        if column is not None and column not in self._engine.headers:
            raise KeyError(f"Unknown column: {column!r}")
        self._active = column

    def render(self) -> str:
        if self._active is None:
            return " " * self._width

        try:
            r = self._engine.result(self._active)
        except RuntimeError:
            return f" [{self._active}] no data computed ".ljust(self._width)

        s = r.summary()
        parts = [f"[{self._active}]"]
        for key in ("sum", "mean", "min", "max", "count"):
            val = s[key]
            if val is None:
                parts.append(f"{key}=—")
            elif val == int(val):
                parts.append(f"{key}={int(val)}")
            else:
                parts.append(f"{key}={val:.4g}")
        line = "  ".join(parts)
        if len(line) > self._width:
            line = line[: self._width - 1] + "…"
        return line.ljust(self._width)

    def __str__(self) -> str:
        return self.render()
