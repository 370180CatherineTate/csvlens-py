"""Renderer that displays formula column results alongside base columns."""
from __future__ import annotations

from typing import Dict, List

from csvlens.column_formula_engine import ColumnFormulaEngine

_ANSI_FORMULA = "\033[36m"   # cyan for formula cells
_ANSI_HEADER  = "\033[33m"   # yellow for formula header
_ANSI_RESET   = "\033[0m"


class ColumnFormulaRenderer:
    """Renders rows with computed formula columns highlighted."""

    def __init__(self, engine: ColumnFormulaEngine, col_width: int = 14) -> None:
        if col_width < 4:
            raise ValueError("col_width must be at least 4")
        self._engine = engine
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _fit(self, text: str) -> str:
        text = str(text) if text is not None else ""
        if len(text) > self._col_width:
            return text[: self._col_width - 1] + "…"
        return text.ljust(self._col_width)

    def render_header(self) -> str:
        """Return a header line with formula column names highlighted."""
        parts = [self._fit(h) for h in self._engine.headers]
        for name in self._engine.formula_names:
            parts.append(f"{_ANSI_HEADER}{self._fit(name)}{_ANSI_RESET}")
        return "  ".join(parts)

    def render_row(self, row: Dict[str, str]) -> str:
        """Render a single row dict, appending evaluated formula values."""
        enriched = self._engine.apply([row])[0]
        parts = [self._fit(enriched.get(h, "")) for h in self._engine.headers]
        for name in self._engine.formula_names:
            val = enriched.get(name, "")
            parts.append(f"{_ANSI_FORMULA}{self._fit(val)}{_ANSI_RESET}")
        return "  ".join(parts)

    def render_all(self, rows: List[Dict[str, str]]) -> str:
        """Render header + all rows as a single string."""
        lines = [self.render_header()]
        for row in rows:
            lines.append(self.render_row(row))
        return "\n".join(lines)
