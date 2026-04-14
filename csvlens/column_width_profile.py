"""Profiles optimal column widths based on content sampling."""

from __future__ import annotations

from typing import List, Dict, Optional


class ColumnWidthProfile:
    """Samples rows to compute recommended display widths per column."""

    MIN_WIDTH: int = 3
    MAX_WIDTH: int = 60

    def __init__(
        self,
        headers: List[str],
        rows: List[Dict[str, str]],
        *,
        min_width: int = MIN_WIDTH,
        max_width: int = MAX_WIDTH,
        sample_size: Optional[int] = None,
    ) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        if min_width < 1:
            raise ValueError("min_width must be >= 1")
        if max_width < min_width:
            raise ValueError("max_width must be >= min_width")

        self._headers = list(headers)
        self._min_width = min_width
        self._max_width = max_width
        sample = rows[:sample_size] if sample_size is not None else rows
        self._widths = self._compute(sample)

    # ------------------------------------------------------------------
    # properties
    # ------------------------------------------------------------------

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def min_width(self) -> int:
        return self._min_width

    @property
    def max_width(self) -> int:
        return self._max_width

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def width_for(self, column: str) -> int:
        """Return the recommended width for *column*."""
        if column not in self._widths:
            raise KeyError(f"Unknown column: {column!r}")
        return self._widths[column]

    def all_widths(self) -> Dict[str, int]:
        """Return a mapping of column -> recommended width."""
        return dict(self._widths)

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _compute(self, rows: List[Dict[str, str]]) -> Dict[str, int]:
        widths: Dict[str, int] = {}
        for col in self._headers:
            best = len(col)  # header length is the baseline
            for row in rows:
                cell = row.get(col, "") or ""
                if len(cell) > best:
                    best = len(cell)
            widths[col] = max(self._min_width, min(self._max_width, best))
        return widths
