"""Status bar summarising active column comparison rules."""
from __future__ import annotations

from typing import Optional

from csvlens.column_compare_engine import ColumnCompareEngine

_BOLD = "\033[1m"
_DIM = "\033[2m"
_RESET = "\033[0m"


class CompareStatusBar:
    """Renders a one-line summary of active comparison rules."""

    def __init__(self, engine: ColumnCompareEngine, width: int = 80) -> None:
        if width < 10:
            raise ValueError("width must be at least 10")
        self._engine = engine
        self._width = width
        self._active_pair: Optional[tuple] = None

    @property
    def width(self) -> int:
        return self._width

    def set_active_pair(self, col_a: str, col_b: str) -> None:
        """Highlight a specific comparison pair in the status bar."""
        key = (col_a, col_b)
        if key not in self._engine.rules:
            raise KeyError(f"no rule for pair {key!r}")
        self._active_pair = key

    def render(self) -> str:
        rules = self._engine.rules
        if not rules:
            msg = "No comparisons active"
            return msg.ljust(self._width)[: self._width]

        parts = []
        for (col_a, col_b), mode in rules.items():
            pair_str = f"{col_a}↔{col_b}[{mode}]"
            if self._active_pair == (col_a, col_b):
                pair_str = f"{_BOLD}{pair_str}{_RESET}"
            parts.append(pair_str)

        prefix = f"{_DIM}CMP:{_RESET} "
        body = "  ".join(parts)
        full = prefix + body
        # Trim to width (ignoring escape codes for a best-effort fit)
        visible = f"CMP: {body}"
        if len(visible) > self._width:
            body = body[: self._width - 6] + "…"
            full = prefix + body
        return full

    def __str__(self) -> str:
        return self.render()
