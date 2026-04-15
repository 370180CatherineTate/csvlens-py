"""A small status bar showing active formula column definitions."""
from __future__ import annotations

from typing import List

from csvlens.column_formula_engine import ColumnFormulaEngine

_ANSI_BOLD  = "\033[1m"
_ANSI_CYAN  = "\033[36m"
_ANSI_DIM   = "\033[2m"
_ANSI_RESET = "\033[0m"


class FormulaStatusBar:
    """Renders a one-line summary of all active formula columns."""

    def __init__(self, engine: ColumnFormulaEngine, width: int = 80) -> None:
        if width < 10:
            raise ValueError("width must be at least 10")
        self._engine = engine
        self._width = width

    @property
    def width(self) -> int:
        return self._width

    def render(self) -> str:
        """Return a fixed-width status line listing formula columns."""
        names = self._engine.formula_names
        if not names:
            label = f"{_ANSI_DIM}[no formulas]{_ANSI_RESET}"
            return label.ljust(self._width)

        parts: List[str] = []
        for name in names:
            expr = self._engine.formulas[name]
            short_expr = expr if len(expr) <= 20 else expr[:19] + "…"
            parts.append(
                f"{_ANSI_CYAN}{_ANSI_BOLD}{name}{_ANSI_RESET}"
                f"{_ANSI_DIM}={short_expr}{_ANSI_RESET}"
            )

        prefix = "Formulas: "
        body = "  |  ".join(parts)
        line = prefix + body
        # Trim to width (ANSI codes are invisible but kept for colour)
        visible = prefix + "  |  ".join(
            f"{n}={self._engine.formulas[n]}" for n in names
        )
        if len(visible) > self._width:
            # Truncate plain representation and re-attach reset
            line = line[: self._width - 1] + "…"
        return line

    def __str__(self) -> str:
        return self.render()
