"""Engine that computes per-cell heat intensity for numeric columns."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


class ColumnHeatmapEngine:
    """Assign a normalised heat value [0.0, 1.0] to every cell in a column."""

    def __init__(self, headers: List[str], rows: List[Dict[str, str]]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._rows = rows
        self._ranges: Dict[str, Tuple[float, float]] = {}
        self._enabled: set = set()
        self._compute_ranges()

    def _compute_ranges(self) -> None:
        for col in self._headers:
            values = [_to_float(r.get(col, "")) for r in self._rows]
            numeric = [v for v in values if v is not None]
            if len(numeric) >= 2:
                self._ranges[col] = (min(numeric), max(numeric))

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def heatmap_columns(self) -> List[str]:
        """Columns that have heatmap enabled and a valid numeric range."""
        return [c for c in self._enabled if c in self._ranges]

    def enable(self, column: str) -> None:
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        self._enabled.add(column)

    def disable(self, column: str) -> None:
        self._enabled.discard(column)

    def heat(self, column: str, value: str) -> Optional[float]:
        """Return normalised heat [0.0, 1.0] or None if not applicable."""
        if column not in self._enabled or column not in self._ranges:
            return None
        v = _to_float(value)
        if v is None:
            return None
        lo, hi = self._ranges[column]
        if hi == lo:
            return 0.5
        return max(0.0, min(1.0, (v - lo) / (hi - lo)))
