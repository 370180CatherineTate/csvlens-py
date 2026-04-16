from __future__ import annotations
from typing import List
from csvlens.column_tag_engine import ColumnTagEngine


class ColumnTagRenderer:
    """Render a tag summary table for columns."""

    def __init__(self, engine: ColumnTagEngine, col_width: int = 18) -> None:
        if col_width < 6:
            raise ValueError("col_width must be at least 6")
        self._engine = engine
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _pad(self, text: str) -> str:
        return text[: self._col_width].ljust(self._col_width)

    def render(self) -> str:
        lines: List[str] = []
        header = self._pad("Column") + "  " + "Tags"
        lines.append(header)
        lines.append("-" * (self._col_width + 2 + 40))
        tags_map = self._engine.tags
        for col in self._engine.headers:
            tag_list = tags_map[col]
            tag_str = ", ".join(tag_list) if tag_list else "(none)"
            lines.append(self._pad(col) + "  " + tag_str)
        return "\n".join(lines)
