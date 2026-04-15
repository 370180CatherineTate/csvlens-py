"""Render a summary table of column aggregates."""
from __future__ import annotations

from typing import List

from csvlens.column_aggregate_engine import ColumnAggregateEngine

_LABELS = ["sum", "mean", "min", "max", "count"]


class ColumnAggregateRenderer:
    """Render aggregate results as a fixed-width text table."""

    def __init__(self, engine: ColumnAggregateEngine, col_width: int = 14) -> None:
        if col_width < 6:
            raise ValueError("col_width must be at least 6")
        self._engine = engine
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _fit(self, text: str) -> str:
        text = str(text)
        if len(text) > self._col_width:
            return text[: self._col_width - 1] + "…"
        return text.ljust(self._col_width)

    def _fmt(self, value: object) -> str:
        if value is None:
            return self._fit("—")
        if isinstance(value, float) and value == int(value):
            return self._fit(str(int(value)))
        if isinstance(value, float):
            return self._fit(f"{value:.4g}")
        return self._fit(str(value))

    def render(self) -> str:
        headers = self._engine.headers
        results = self._engine.all_results()

        # Header row
        label_w = 7
        header_line = " " * label_w + " ".join(self._fit(h) for h in headers)
        lines = [header_line, "-" * len(header_line)]

        for label in _LABELS:
            row_parts = [label.ljust(label_w)]
            for h in headers:
                if h in results:
                    val = results[h].summary().get(label)
                    row_parts.append(self._fmt(val))
                else:
                    row_parts.append(self._fit("—"))
            lines.append(" ".join(row_parts))

        return "\n".join(lines)
