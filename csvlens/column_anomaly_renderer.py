"""Renders anomaly detection results as a formatted table row."""
from __future__ import annotations
from typing import List, Dict
from csvlens.column_anomaly_engine import ColumnAnomalyEngine


class ColumnAnomalyRenderer:
    _ANSI_RED = "\033[31m"
    _ANSI_GREEN = "\033[32m"
    _ANSI_RESET = "\033[0m"

    def __init__(self, engine: ColumnAnomalyEngine, col_width: int = 18) -> None:
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

    def render_header(self) -> str:
        cells = [self._fit(h) for h in self._engine.headers]
        return " | ".join(cells)

    def render_row(self, row: Dict[str, str]) -> str:
        parts: List[str] = []
        for col in self._engine.headers:
            result = self._engine.get(col)
            raw = row.get(col, "")
            if result.iqr is not None and result.q1 is not None and result.q3 is not None:
                from csvlens.column_anomaly_engine import _to_float
                val = _to_float(raw)
                lo = result.q1 - self._engine.multiplier * result.iqr
                hi = result.q3 + self._engine.multiplier * result.iqr
                if val is not None and (val < lo or val > hi):
                    cell = self._ANSI_RED + self._fit(raw) + self._ANSI_RESET
                else:
                    cell = self._fit(raw)
            else:
                cell = self._fit(raw)
            parts.append(cell)
        return " | ".join(parts)

    def render_summary(self) -> str:
        lines = []
        for col in self._engine.headers:
            lines.append(self._engine.get(col).summary)
        return "\n".join(lines)
