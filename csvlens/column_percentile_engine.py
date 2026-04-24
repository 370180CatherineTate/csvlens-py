"""Compute per-column percentile statistics for numeric columns."""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence


def _to_float(value: str) -> Optional[float]:
    """Return float or None if conversion fails."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


class PercentileResult:
    """Percentile statistics for a single column."""

    def __init__(
        self,
        column: str,
        values: List[float],
        percentiles: Sequence[int],
    ) -> None:
        self._column = column
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        self._data: Dict[int, Optional[float]] = {}
        for p in percentiles:
            if n == 0:
                self._data[p] = None
            else:
                idx = (p / 100) * (n - 1)
                lo = int(idx)
                hi = min(lo + 1, n - 1)
                frac = idx - lo
                self._data[p] = sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac
        self._count = n

    @property
    def column(self) -> str:
        return self._column

    @property
    def count(self) -> int:
        return self._count

    def get(self, percentile: int) -> Optional[float]:
        """Return the value at the given percentile, or None if unavailable."""
        return self._data.get(percentile)

    def summary(self) -> Dict[str, object]:
        result: Dict[str, object] = {"column": self._column, "count": self._count}
        for p, v in self._data.items():
            result[f"p{p}"] = round(v, 6) if v is not None else None
        return result


class ColumnPercentileEngine:
    """Compute configurable percentiles for every numeric column."""

    _DEFAULT_PERCENTILES = (10, 25, 50, 75, 90)

    def __init__(
        self,
        headers: List[str],
        rows: List[Dict[str, str]],
        percentiles: Sequence[int] = _DEFAULT_PERCENTILES,
    ) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        if not all(0 <= p <= 100 for p in percentiles):
            raise ValueError("all percentile values must be between 0 and 100")
        self._headers = list(headers)
        self._percentiles = list(percentiles)
        self._results: Dict[str, PercentileResult] = {}
        self._compute(rows)

    def _compute(self, rows: List[Dict[str, str]]) -> None:
        buckets: Dict[str, List[float]] = {h: [] for h in self._headers}
        for row in rows:
            for h in self._headers:
                v = _to_float(row.get(h, ""))
                if v is not None:
                    buckets[h].append(v)
        for h in self._headers:
            self._results[h] = PercentileResult(h, buckets[h], self._percentiles)

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def percentiles(self) -> List[int]:
        return list(self._percentiles)

    @property
    def results(self) -> Dict[str, PercentileResult]:
        return dict(self._results)

    def get(self, column: str) -> PercentileResult:
        if column not in self._results:
            raise KeyError(f"unknown column: {column!r}")
        return self._results[column]
