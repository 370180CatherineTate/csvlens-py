"""ColumnHistogram: compute ASCII histogram buckets for a numeric column."""

from __future__ import annotations

from typing import Dict, List, Optional


BARS = "▁▂▃▄▅▆▇█"


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value.strip())
    except (ValueError, AttributeError):
        return None


class ColumnHistogram:
    """Compute a fixed-width histogram for a numeric CSV column."""

    def __init__(
        self,
        headers: List[str],
        rows: List[Dict[str, str]],
        *,
        num_bins: int = 8,
    ) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        if num_bins < 2:
            raise ValueError("num_bins must be at least 2")
        self._headers: List[str] = list(headers)
        self._rows = rows
        self._num_bins = num_bins
        self._cache: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def num_bins(self) -> int:
        return self._num_bins

    def render(self, column: str) -> str:
        """Return an 8-character bar string for *column*, or '' if non-numeric."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        if column in self._cache:
            return self._cache[column]
        result = self._compute(column)
        self._cache[column] = result
        return result

    def summary(self, column: str) -> Dict[str, object]:
        """Return min, max, mean and the bar string for *column*."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        values = [v for v in (_to_float(r.get(column, "")) for r in self._rows) if v is not None]
        if not values:
            return {"min": None, "max": None, "mean": None, "bar": ""}
        return {
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "bar": self.render(column),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _compute(self, column: str) -> str:
        values = [v for v in (_to_float(r.get(column, "")) for r in self._rows) if v is not None]
        if not values:
            return ""
        lo, hi = min(values), max(values)
        if lo == hi:
            return BARS[-1] * self._num_bins
        width = (hi - lo) / self._num_bins
        counts = [0] * self._num_bins
        for v in values:
            idx = min(int((v - lo) / width), self._num_bins - 1)
            counts[idx] += 1
        peak = max(counts)
        bar = "".join(BARS[min(int(c / peak * (len(BARS) - 1)), len(BARS) - 1)] for c in counts)
        return bar
