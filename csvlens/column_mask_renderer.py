"""Renderer that displays masked-column indicators in a header / data row."""
from __future__ import annotations

from typing import Dict, List

from csvlens.column_mask_engine import ColumnMaskEngine

_ANSI_MASK = "\033[2;33m"  # dim yellow for masked placeholder
_ANSI_RESET = "\033[0m"


class ColumnMaskRenderer:
    """Render rows applying column masking with optional ANSI colouring."""

    def __init__(
        self,
        engine: ColumnMaskEngine,
        col_width: int = 12,
        coloured: bool = True,
    ) -> None:
        if col_width < 3:
            raise ValueError("col_width must be at least 3")
        self._engine = engine
        self._col_width = col_width
        self._coloured = coloured

    @property
    def col_width(self) -> int:
        return self._col_width

    def _fit(self, text: str) -> str:
        w = self._col_width
        if len(text) > w:
            return text[: w - 1] + "…"
        return text.ljust(w)

    def render_header(self) -> str:
        parts: List[str] = []
        for h in self._engine.headers:
            cell = self._fit(h)
            if self._coloured and self._engine.is_masked(h):
                cell = f"\033[4;33m{cell}{_ANSI_RESET}"  # underline yellow = masked col
            parts.append(cell)
        return " | ".join(parts)

    def render_row(self, row: Dict[str, str]) -> str:
        masked = self._engine.apply(row)
        parts: List[str] = []
        for h in self._engine.headers:
            raw = masked.get(h, "")
            cell = self._fit(raw)
            if self._coloured and self._engine.is_masked(h):
                cell = f"{_ANSI_MASK}{cell}{_ANSI_RESET}"
            parts.append(cell)
        return " | ".join(parts)

    def render_all(self, rows: List[Dict[str, str]]) -> str:
        lines = [self.render_header()]
        lines.extend(self.render_row(r) for r in rows)
        return "\n".join(lines)
