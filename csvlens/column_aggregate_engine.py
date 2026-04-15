"""Compute per-column aggregate values (sum, mean, min, max, count) over a set of rows."""
from __future__ import annotations

from typing import Dict, List, Optional


class AggregateResult:
    """Holds aggregate statistics for a single column."""

    def __init__(self, col: str, values: List[float]) -> None:
        self.column = col
        self._n = len(values)
        if self._n == 0:
            self.total = self.mean = self.minimum = self.maximum = None
        else:
            self.total = sum(values)
            self.mean = self.total / self._n
            self.minimum = min(values)
            self.maximum = max(values)

    @property
    def numeric_count(self) -> int:
        return self._n

    def summary(self) -> Dict[str, Optional[float]]:
        return {
            "sum": self.total,
            "mean": self.mean,
            "min": self.minimum,
            "max": self.maximum,
            "count": float(self._n),
        }


class ColumnAggregateEngine:
    """Compute aggregates for selected columns across a list of row dicts."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers = list(headers)
        self._results: Dict[str, AggregateResult] = {}

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    def compute(self, rows: List[Dict[str, str]]) -> None:
        """Run aggregation over *rows* for all headers."""
        buckets: Dict[str, List[float]] = {h: [] for h in self._headers}
        for row in rows:
            for h in self._headers:
                raw = row.get(h, "")
                try:
                    buckets[h].append(float(raw))
                except (ValueError, TypeError):
                    pass
        self._results = {h: AggregateResult(h, buckets[h]) for h in self._headers}

    def result(self, column: str) -> AggregateResult:
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        if column not in self._results:
            raise RuntimeError("Call compute() before accessing results")
        return self._results[column]

    def all_results(self) -> Dict[str, AggregateResult]:
        return dict(self._results)
