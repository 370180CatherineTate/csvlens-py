"""Renderer for column comparison results."""
from __future__ import annotations

from typing import List, Dict, Tuple

from csvlens.column_compare_engine import ColumnCompareEngine, CompareResult

_GREEN = "\033[32m"
_RED = "\033[31m"
_CYAN = "\033[36m"
_RESET = "\033[0m"


class ColumnCompareRenderer:
    def __init__(self, engine: ColumnCompareEngine, col_width: int = 14) -> None:
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

    def _colour(self, result: CompareResult) -> str:
        label = result.label()
        if result.diff is not None:
            colour = _CYAN
        elif result.match is True:
            colour = _GREEN
        elif result.match is False:
            colour = _RED
        else:
            colour = ""
        if colour:
            return f"{colour}{self._fit(label)}{_RESET}"
        return self._fit(label)

    def render_header(self) -> str:
        parts: List[str] = []
        for col_a, col_b in self._engine.rules:
            label = f"{col_a}↔{col_b}"
            parts.append(self._fit(label))
        return "  ".join(parts)

    def render_row(self, row: Dict[str, str]) -> str:
        results = self._engine.compare_row(row)
        parts: List[str] = []
        for key in self._engine.rules:
            result = results.get(key)
            if result is None:
                parts.append(self._fit(""))
            else:
                parts.append(self._colour(result))
        return "  ".join(parts)

    def render_all(
        self, rows: List[Dict[str, str]]
    ) -> str:
        lines = [self.render_header()]
        for row in rows:
            lines.append(self.render_row(row))
        return "\n".join(lines)
