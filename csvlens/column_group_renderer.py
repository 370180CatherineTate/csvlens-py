"""Renders a header row with group labels and expansion indicators."""

from __future__ import annotations
from typing import List

from csvlens.column_group_engine import ColumnGroupEngine

_ANSI_RESET = "\033[0m"
_ANSI_BOLD = "\033[1m"
_ANSI_CYAN = "\033[36m"
_ANSI_DIM = "\033[2m"


class ColumnGroupRenderer:
    """Renders visible headers, highlighting group placeholders."""

    def __init__(self, engine: ColumnGroupEngine, col_width: int = 14) -> None:
        if not isinstance(engine, ColumnGroupEngine):
            raise TypeError("engine must be a ColumnGroupEngine instance")
        if col_width < 4:
            raise ValueError("col_width must be >= 4")
        self._engine = engine
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _pad(self, text: str) -> str:
        return text[: self._col_width].ljust(self._col_width)

    def _is_placeholder(self, label: str) -> bool:
        return label.startswith("[") and label.endswith("]")

    def render_header(self) -> str:
        """Return a single formatted header line."""
        parts: List[str] = []
        for label in self._engine.visible_headers():
            cell = self._pad(label)
            if self._is_placeholder(label):
                parts.append(f"{_ANSI_BOLD}{_ANSI_CYAN}{cell}{_ANSI_RESET}")
            else:
                parts.append(f"{_ANSI_BOLD}{cell}{_ANSI_RESET}")
        return " | ".join(parts)

    def render_group_summary(self) -> str:
        """Return a summary line listing all groups and their state."""
        if not self._engine.group_names:
            return _ANSI_DIM + "(no groups defined)" + _ANSI_RESET
        lines: List[str] = []
        for gname in self._engine.group_names:
            cols = self._engine.groups[gname]
            state = "collapsed" if self._engine.is_collapsed(gname) else "expanded"
            lines.append(f"{gname} [{state}]: {', '.join(cols)}")
        return "\n".join(lines)

    def render(self) -> str:
        """Return header + group summary separated by a newline."""
        header = self.render_header()
        summary = self.render_group_summary()
        return f"{header}\n{summary}"
