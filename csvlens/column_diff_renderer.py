"""Render column diff summary as a formatted table."""
from __future__ import annotations
from typing import Dict, List
from csvlens.column_diff_profile import ColumnDiffProfile

_RESET = "\033[0m"
_RED = "\033[31m"
_GREEN = "\033[32m"


class ColumnDiffRenderer:
    def __init__(self, profile: ColumnDiffProfile, col_width: int = 18) -> None:
        if col_width < 6:
            raise ValueError("col_width must be at least 6")
        self._profile = profile
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _fit(self, text: str) -> str:
        if len(text) > self._col_width:
            return text[: self._col_width - 1] + "…"
        return text.ljust(self._col_width)

    def render(self, name_a: str, name_b: str) -> str:
        summary = self._profile.diff_summary(name_a, name_b)
        lines: List[str] = []
        header = self._fit("Column") + "  " + self._fit("Changed Rows")
        lines.append(header)
        lines.append("-" * (self._col_width * 2 + 2))
        for col, count in summary.items():
            colour = _RED if count > 0 else _GREEN
            col_cell = self._fit(col)
            count_cell = colour + self._fit(str(count)) + _RESET
            lines.append(col_cell + "  " + count_cell)
        return "\n".join(lines)
