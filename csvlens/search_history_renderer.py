"""Renders a search history list for display in the TUI."""
from __future__ import annotations
from typing import List
from csvlens.column_search_history import ColumnSearchHistory


class SearchHistoryRenderer:
    """Renders global or per-column search history as a formatted string block."""

    def __init__(self, history: ColumnSearchHistory, col_width: int = 40) -> None:
        if col_width < 8:
            raise ValueError("col_width must be at least 8")
        self._history = history
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _pad(self, text: str) -> str:
        if len(text) > self._col_width:
            return text[: self._col_width - 1] + "…"
        return text.ljust(self._col_width)

    def render_global(self, max_items: int = 10) -> str:
        """Render global history as a numbered list string."""
        items = self._history.global_history()[:max_items]
        if not items:
            return self._pad("(no history)")
        lines: List[str] = []
        for i, pattern in enumerate(items, 1):
            lines.append(self._pad(f"{i:>2}. {pattern}"))
        return "\n".join(lines)

    def render_column(self, column: str, max_items: int = 10) -> str:
        """Render per-column history as a numbered list string."""
        items = self._history.column_history(column)[:max_items]
        header = self._pad(f"[{column}]")
        if not items:
            return header + "\n" + self._pad("(no history)")
        lines: List[str] = [header]
        for i, pattern in enumerate(items, 1):
            lines.append(self._pad(f"{i:>2}. {pattern}"))
        return "\n".join(lines)

    def render(self, column: str | None = None, max_items: int = 10) -> str:
        """Render global history or column history depending on argument."""
        if column is None:
            return self.render_global(max_items)
        return self.render_column(column, max_items)
