from __future__ import annotations

from typing import Dict, List

from csvlens.column_validation_engine import ColumnValidationEngine

_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RESET = "\033[0m"


class ColumnValidationRenderer:
    """Renders validation results as a formatted table."""

    def __init__(self, engine: ColumnValidationEngine, col_width: int = 18) -> None:
        if col_width < 6:
            raise ValueError("col_width must be at least 6")
        self._engine = engine
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _fit(self, text: str) -> str:
        if len(text) > self._col_width:
            return text[: self._col_width - 1] + "…"
        return text.ljust(self._col_width)

    def render_header(self) -> str:
        parts = [self._fit(h) for h in self._engine.headers]
        return "  ".join(parts)

    def render_row(
        self, row: Dict[str, str], errors: Dict[str, List[str]]
    ) -> str:
        parts = []
        for h in self._engine.headers:
            cell = row.get(h, "")
            fitted = self._fit(cell)
            if h in errors:
                parts.append(f"{_RED}{fitted}{_RESET}")
            else:
                parts.append(f"{_GREEN}{fitted}{_RESET}")
        return "  ".join(parts)

    def render_summary(
        self, error_rows: list
    ) -> str:
        """Render a summary line: total invalid rows and affected columns."""
        if not error_rows:
            return f"{_GREEN}All rows valid.{_RESET}"
        total = len(error_rows)
        cols: set = set()
        for _, errs in error_rows:
            cols.update(errs.keys())
        col_list = ", ".join(sorted(cols))
        return (
            f"{_YELLOW}{total} invalid row(s) "
            f"in column(s): {col_list}{_RESET}"
        )
