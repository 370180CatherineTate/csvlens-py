from __future__ import annotations

from typing import List

from csvlens.column_variance_engine import ColumnVarianceEngine


class ColumnVarianceRenderer:
    """Renders variance statistics for each column as a formatted table."""

    _ANSI_RESET = "\033[0m"
    _ANSI_HEADER = "\033[1;36m"
    _ANSI_LOW = "\033[32m"
    _ANSI_HIGH = "\033[31m"
    _ANSI_NA = "\033[90m"

    def __init__(self, engine: ColumnVarianceEngine, col_width: int = 14) -> None:
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
        h = self._ANSI_HEADER
        r = self._ANSI_RESET
        cols = ["Column", "Mean", "Variance", "Std Dev", "CV"]
        return "  ".join(f"{h}{self._fit(c)}{r}" for c in cols)

    def render_row(self, column: str) -> str:
        result = self._engine.get(column)
        if result.variance is None:
            colour = self._ANSI_NA
            parts = [
                self._fit(column),
                self._fit("N/A"),
                self._fit("N/A"),
                self._fit("N/A"),
                self._fit("N/A"),
            ]
        else:
            colour = self._ANSI_LOW if result.cv is None or result.cv < 1.0 else self._ANSI_HIGH
            cv_str = f"{result.cv:.4f}" if result.cv is not None else "N/A"
            parts = [
                self._fit(column),
                self._fit(f"{result.mean:.4f}"),
                self._fit(f"{result.variance:.4f}"),
                self._fit(f"{result.std_dev:.4f}"),
                self._fit(cv_str),
            ]
        r = self._ANSI_RESET
        return "  ".join(f"{colour}{p}{r}" for p in parts)

    def render(self) -> str:
        lines: List[str] = [self.render_header()]
        for col in self._engine.headers:
            lines.append(self.render_row(col))
        return "\n".join(lines)
