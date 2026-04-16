from __future__ import annotations
from csvlens.column_tag_engine import ColumnTagEngine


class TagStatusBar:
    """One-line status bar summarising active tag filter."""

    def __init__(self, engine: ColumnTagEngine, width: int = 80) -> None:
        if width < 10:
            raise ValueError("width must be at least 10")
        self._engine = engine
        self._width = width
        self._active_tag: str | None = None

    @property
    def width(self) -> int:
        return self._width

    def set_active_tag(self, tag: str | None) -> None:
        self._active_tag = tag

    def render(self) -> str:
        if self._active_tag is None:
            msg = "Tags: (no filter active)"
        else:
            cols = self._engine.columns_with_tag(self._active_tag)
            col_str = ", ".join(cols) if cols else "(no columns)"
            msg = f"Tag filter: {self._active_tag!r}  →  {col_str}"
        return msg[: self._width].ljust(self._width)

    def __str__(self) -> str:
        return self.render()
