from __future__ import annotations

from typing import List, Optional

from csvlens.column_correlation_engine import ColumnCorrelationEngine, CorrelationResult


class ColumnCorrelationRenderer:
    """Render a correlation result as a formatted text block."""

    _COLOUR_POS = "\033[32m"   # green
    _COLOUR_NEG = "\033[31m"   # red
    _COLOUR_NA  = "\033[90m"   # dark grey
    _RESET      = "\033[0m"

    def __init__(self, engine: ColumnCorrelationEngine, col_width: int = 20) -> None:
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

    def _colour(self, result: CorrelationResult) -> str:
        if result.r is None:
            return self._COLOUR_NA
        return self._COLOUR_POS if result.r >= 0 else self._COLOUR_NEG

    def render_header(self) -> str:
        parts = [
            self._fit("Column A"),
            self._fit("Column B"),
            self._fit("r"),
            self._fit("Strength"),
            self._fit("n"),
        ]
        return "  ".join(parts)

    def render_result(self, result: CorrelationResult) -> str:
        r_str = f"{result.r:.4f}" if result.r is not None else "n/a"
        colour = self._colour(result)
        parts = [
            self._fit(result.col_a),
            self._fit(result.col_b),
            colour + self._fit(r_str) + self._RESET,
            self._fit(result.strength),
            self._fit(str(result.n)),
        ]
        return "  ".join(parts)

    def render(self, col_a: str, col_b: str) -> str:
        result = self._engine.compute(col_a, col_b)
        lines = [self.render_header(), self.render_result(result)]
        return "\n".join(lines)
