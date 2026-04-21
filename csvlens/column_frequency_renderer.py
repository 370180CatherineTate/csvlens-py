from __future__ import annotations

from typing import List

from csvlens.column_frequency_engine import ColumnFrequencyEngine


class ColumnFrequencyRenderer:
    """Renders a frequency-distribution table for a single column."""

    _ANSI_RESET = "\033[0m"
    _ANSI_BOLD = "\033[1m"
    _ANSI_CYAN = "\033[36m"

    def __init__(
        self,
        engine: ColumnFrequencyEngine,
        col_width: int = 20,
        top_n: int = 10,
    ) -> None:
        if col_width < 4:
            raise ValueError("col_width must be at least 4")
        if top_n < 1:
            raise ValueError("top_n must be at least 1")
        self._engine = engine
        self._col_width = col_width
        self._top_n = top_n

    @property
    def col_width(self) -> int:
        return self._col_width

    def _fit(self, text: str) -> str:
        if len(text) > self._col_width:
            return text[: self._col_width - 1] + "…"
        return text.ljust(self._col_width)

    def render(self, column: str) -> str:
        """Return a multi-line string showing the top-N frequency table."""
        result = self._engine.compute(column)
        lines: List[str] = []
        header = (
            f"{self._ANSI_BOLD}{self._ANSI_CYAN}"
            f"Frequency: {column} "
            f"({result.unique_count()} unique / {result.total} rows)"
            f"{self._ANSI_RESET}"
        )
        lines.append(header)
        lines.append("-" * (self._col_width + 18))
        for val, cnt, pct in result.top(self._top_n):
            display = self._fit(repr(val) if val == "" else val)
            lines.append(f"  {display}  {cnt:>6}  {pct:>6.1f}%")
        return "\n".join(lines)
