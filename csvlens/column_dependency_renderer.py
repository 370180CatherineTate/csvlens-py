"""Render a column-dependency summary as a formatted string table."""
from __future__ import annotations

from typing import List

from csvlens.column_dependency_engine import ColumnDependencyEngine


class ColumnDependencyRenderer:
    """Render dependency information for a given column."""

    _HEADER_LABEL = "Column"
    _DEPS_LABEL = "Depends On"
    _DEPENDENTS_LABEL = "Used By"

    def __init__(self, engine: ColumnDependencyEngine, col_width: int = 20) -> None:
        if col_width < 6:
            raise ValueError("col_width must be at least 6")
        self._engine = engine
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _pad(self, text: str) -> str:
        text = text[: self._col_width]
        return text.ljust(self._col_width)

    def _fmt_list(self, items: List[str]) -> str:
        if not items:
            return "(none)"
        joined = ", ".join(items)
        if len(joined) > self._col_width:
            joined = joined[: self._col_width - 1] + "…"
        return joined

    # ------------------------------------------------------------------
    # public
    # ------------------------------------------------------------------

    def render(self, column: str, transitive: bool = False) -> str:
        """Render a two-section summary for *column*.

        Parameters
        ----------
        column:
            The column whose dependency information should be rendered.
        transitive:
            When *True*, show transitive dependencies instead of direct ones.
        """
        if transitive:
            deps = self._engine.transitive_dependencies(column)
            deps_label = "Trans. Deps"
        else:
            deps = self._engine.direct_dependencies(column)
            deps_label = self._DEPS_LABEL

        dependents = self._engine.dependents(column)

        sep = "-" * (self._col_width * 2 + 3)
        lines: List[str] = [
            f"{self._pad(self._HEADER_LABEL)} | {self._pad('Value')}",
            sep,
            f"{self._pad('Column')} | {self._pad(column)}",
            f"{self._pad(deps_label)} | {self._fmt_list(deps)}",
            f"{self._pad(self._DEPENDENTS_LABEL)} | {self._fmt_list(dependents)}",
        ]
        return "\n".join(lines)
