from __future__ import annotations
from typing import Dict, List, Optional


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


class ColumnProgressEngine:
    """Computes per-column progress bars based on value relative to a max."""

    def __init__(self, headers: List[str], rows: List[Dict[str, str]]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers = list(headers)
        self._rows = rows
        self._overrides: Dict[str, float] = {}
        self._maxima: Dict[str, Optional[float]] = self._compute_maxima()

    def _compute_maxima(self) -> Dict[str, Optional[float]]:
        maxima: Dict[str, Optional[float]] = {}
        for h in self._headers:
            vals = [_to_float(r.get(h, "")) for r in self._rows]
            nums = [v for v in vals if v is not None]
            maxima[h] = max(nums) if nums else None
        return maxima

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    def set_max(self, column: str, value: float) -> None:
        if column not in self._headers:
            raise KeyError(f"unknown column: {column!r}")
        if value <= 0:
            raise ValueError("max value must be positive")
        self._overrides[column] = value

    def clear_max(self, column: str) -> None:
        self._overrides.pop(column, None)

    def effective_max(self, column: str) -> Optional[float]:
        if column in self._overrides:
            return self._overrides[column]
        return self._maxima.get(column)

    def progress(self, column: str, raw_value: str) -> Optional[float]:
        """Return a fraction [0.0, 1.0] or None if not computable."""
        if column not in self._headers:
            raise KeyError(f"unknown column: {column!r}")
        val = _to_float(raw_value)
        if val is None:
            return None
        mx = self.effective_max(column)
        if mx is None or mx == 0:
            return None
        return max(0.0, min(1.0, val / mx))
