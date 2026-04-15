"""FreezeRenderer: render a table row with frozen-column visual separator."""

from __future__ import annotations

from typing import Dict, List, Optional

from csvlens.freeze_engine import FreezeEngine

_SEP = "│"  # Unicode box-drawing separator


class FreezeRenderer:
    """Renders a single row as a list of cell strings, inserting a visual
    separator between the frozen and unfrozen column groups.

    Parameters
    ----------
    engine:
        A configured :class:`FreezeEngine` instance.
    col_width:
        Fixed width used to pad/truncate every cell.  Defaults to 12.
    separator:
        String inserted between frozen and unfrozen groups when at least
        one column is frozen.  Defaults to the ``│`` box-drawing char.
    """

    def __init__(
        self,
        engine: FreezeEngine,
        col_width: int = 12,
        separator: str = _SEP,
    ) -> None:
        if col_width < 1:
            raise ValueError("col_width must be >= 1")
        self._engine = engine
        self._col_width = col_width
        self._separator = separator

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def col_width(self) -> int:
        return self._col_width

    @property
    def separator(self) -> str:
        return self._separator

    def render_cells(self, row: Dict[str, str]) -> List[str]:
        """Return an ordered list of formatted cell strings.

        If any columns are frozen a separator string is inserted between
        the frozen group and the unfrozen group.
        """
        cells: List[str] = []
        frozen = self._engine.frozen
        unfrozen = self._engine.unfrozen

        for col in frozen:
            cells.append(self._fmt(row.get(col, "")))

        if frozen and unfrozen:
            cells.append(self._separator)

        for col in unfrozen:
            cells.append(self._fmt(row.get(col, "")))

        return cells

    def render_str(self, row: Dict[str, str], delimiter: str = " ") -> str:
        """Return a single string joining all cells with *delimiter*."""
        return delimiter.join(self.render_cells(row))

    def render_header(self) -> List[str]:
        """Return formatted header cells in frozen-first order."""
        ordered = self._engine.ordered_headers()
        frozen = self._engine.frozen
        unfrozen = self._engine.unfrozen

        cells: List[str] = [self._fmt(h) for h in frozen]
        if frozen and unfrozen:
            cells.append(self._separator)
        cells += [self._fmt(h) for h in unfrozen]
        return cells

    def render_rows(self, rows: List[Dict[str, str]], delimiter: str = " ") -> List[str]:
        """Render multiple rows as strings, each joined with *delimiter*.

        Parameters
        ----------
        rows:
            A list of row dicts mapping column name to cell value.
        delimiter:
            String used to join cells within each row.  Defaults to a
            single space.

        Returns
        -------
        List[str]
            One rendered string per input row, in the same order.
        """
        return [self.render_str(row, delimiter=delimiter) for row in rows]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _fmt(self, value: str) -> str:
        """Truncate or left-pad *value* to exactly *col_width* characters."""
        value = str(value)
        if len(value) > self._col_width:
            return value[: self._col_width]
        return value.ljust(self._col_width)
