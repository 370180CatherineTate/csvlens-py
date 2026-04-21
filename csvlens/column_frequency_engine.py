from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional


class FrequencyResult:
    """Holds frequency distribution for a single column."""

    def __init__(self, column: str, counts: Counter, total: int) -> None:
        self._column = column
        self._counts = counts
        self._total = total

    @property
    def column(self) -> str:
        return self._column

    @property
    def total(self) -> int:
        return self._total

    def top(self, n: int = 10) -> List[tuple]:
        """Return the top-n (value, count, pct) tuples sorted by count desc."""
        if n < 1:
            raise ValueError("n must be at least 1")
        return [
            (val, cnt, round(cnt / self._total * 100, 1) if self._total else 0.0)
            for val, cnt in self._counts.most_common(n)
        ]

    def unique_count(self) -> int:
        return len(self._counts)


class ColumnFrequencyEngine:
    """Computes value-frequency distributions for CSV columns."""

    def __init__(self, headers: List[str], rows: List[Dict[str, str]]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers = list(headers)
        self._rows = rows
        self._cache: Dict[str, FrequencyResult] = {}

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    def compute(self, column: str) -> FrequencyResult:
        """Return a FrequencyResult for *column*, computing lazily."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        if column not in self._cache:
            counts: Counter = Counter()
            for row in self._rows:
                val = row.get(column, "") or ""
                counts[val] += 1
            self._cache[column] = FrequencyResult(column, counts, len(self._rows))
        return self._cache[column]

    def invalidate(self, column: Optional[str] = None) -> None:
        """Clear cached results for *column*, or all columns if None."""
        if column is None:
            self._cache.clear()
        else:
            self._cache.pop(column, None)
