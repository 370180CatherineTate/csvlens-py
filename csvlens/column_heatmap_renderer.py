"""Renderer that applies ANSI background colour based on heat intensity."""
from __future__ import annotations

from typing import Dict, List, Optional

from csvlens.column_heatmap_engine import ColumnHeatmapEngine

# ANSI 256-colour background escape
_BG = "\x1b[48;5;{}m"
_RESET = "\x1b[0m"

# Gradient from cool (blue-ish) to hot (red-ish) using 256-colour indices
_GRADIENT = [17, 18, 19, 20, 21, 27, 33, 39, 45, 51,
             50, 49, 48, 47, 46, 82, 118, 154, 190, 226,
             220, 214, 208, 202, 196]


class ColumnHeatmapRenderer:
    """Render table rows with heatmap colouring on numeric columns."""

    def __init__(self, engine: ColumnHeatmapEngine, col_width: int = 12) -> None:
        if col_width < 1:
            raise ValueError("col_width must be >= 1")
        self._engine = engine
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _fit(self, text: str) -> str:
        if len(text) > self._col_width:
            return text[: self._col_width - 1] + "…"
        return text.ljust(self._col_width)

    def _colour_cell(self, text: str, heat: Optional[float]) -> str:
        fitted = self._fit(text)
        if heat is None:
            return fitted
        idx = int(heat * (len(_GRADIENT) - 1))
        colour = _GRADIENT[max(0, min(len(_GRADIENT) - 1, idx))]
        return f"{_BG.format(colour)}{fitted}{_RESET}"

    def render_header(self) -> str:
        parts = [self._fit(h) for h in self._engine.headers]
        return " | ".join(parts)

    def render_row(self, row: Dict[str, str]) -> str:
        parts = []
        for col in self._engine.headers:
            val = row.get(col, "")
            heat = self._engine.heat(col, val)
            parts.append(self._colour_cell(val, heat))
        return " | ".join(parts)
