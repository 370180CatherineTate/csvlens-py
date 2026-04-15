"""Renderer that applies conditional formatting when displaying CSV rows."""
from __future__ import annotations

from typing import Dict, List

from csvlens.column_conditional_format import ColumnConditionalFormat


class ConditionalFormatRenderer:
    """Render a row of cells with conditional colour rules applied."""

    def __init__(self, fmt: ColumnConditionalFormat, col_width: int = 12) -> None:
        if col_width < 1:
            raise ValueError("col_width must be >= 1")
        self._fmt = fmt
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _fit(self, text: str) -> str:
        """Truncate or pad *text* to col_width (ignoring embedded ANSI codes for width)."""
        # Strip ANSI for length measurement
        import re
        plain = re.sub(r"\033\[[0-9;]*m", "", text)
        if len(plain) > self._col_width:
            # Truncate the *raw* text before colouring
            text = text[: self._col_width]
        return text.ljust(self._col_width) if len(plain) <= self._col_width else text

    def render_header(self) -> str:
        """Return a header row string with column names padded to col_width."""
        parts = [h[: self._col_width].ljust(self._col_width) for h in self._fmt.headers]
        return "  ".join(parts)

    def render_row(self, row: Dict[str, str]) -> str:
        """Return a formatted row string with conditional colours applied."""
        parts: List[str] = []
        for header in self._fmt.headers:
            raw = row.get(header, "")
            coloured = self._fmt.format_cell(header, raw)
            parts.append(self._fit(coloured))
        return "  ".join(parts)

    def render_all(self, rows: List[Dict[str, str]]) -> str:
        """Render header + all rows joined by newlines."""
        lines = [self.render_header()]
        for row in rows:
            lines.append(self.render_row(row))
        return "\n".join(lines)
