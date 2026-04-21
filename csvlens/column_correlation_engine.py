from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


class CorrelationResult:
    """Pearson correlation coefficient between two columns."""

    def __init__(self, col_a: str, col_b: str, r: Optional[float], n: int) -> None:
        self._col_a = col_a
        self._col_b = col_b
        self._r = r
        self._n = n

    @property
    def col_a(self) -> str:
        return self._col_a

    @property
    def col_b(self) -> str:
        return self._col_b

    @property
    def r(self) -> Optional[float]:
        return self._r

    @property
    def n(self) -> int:
        return self._n

    @property
    def strength(self) -> str:
        if self._r is None:
            return "n/a"
        a = abs(self._r)
        if a >= 0.9:
            return "very strong"
        if a >= 0.7:
            return "strong"
        if a >= 0.4:
            return "moderate"
        if a >= 0.2:
            return "weak"
        return "negligible"


class ColumnCorrelationEngine:
    """Compute Pearson correlations between pairs of numeric columns."""

    def __init__(self, headers: List[str], rows: List[Dict[str, str]]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers = list(headers)
        self._rows = rows
        self._cache: Dict[Tuple[str, str], CorrelationResult] = {}

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    def compute(self, col_a: str, col_b: str) -> CorrelationResult:
        if col_a not in self._headers:
            raise KeyError(f"Unknown column: {col_a!r}")
        if col_b not in self._headers:
            raise KeyError(f"Unknown column: {col_b!r}")
        key = (col_a, col_b)
        if key not in self._cache:
            self._cache[key] = self._pearson(col_a, col_b)
        return self._cache[key]

    def _pearson(self, col_a: str, col_b: str) -> CorrelationResult:
        pairs = [
            (xa, xb)
            for row in self._rows
            for xa, xb in [(_to_float(row.get(col_a, "")), _to_float(row.get(col_b, "")))] 
            if xa is not None and xb is not None
        ]
        n = len(pairs)
        if n < 2:
            return CorrelationResult(col_a, col_b, None, n)
        mean_a = sum(x for x, _ in pairs) / n
        mean_b = sum(y for _, y in pairs) / n
        num = sum((x - mean_a) * (y - mean_b) for x, y in pairs)
        den_a = math.sqrt(sum((x - mean_a) ** 2 for x, _ in pairs))
        den_b = math.sqrt(sum((y - mean_b) ** 2 for _, y in pairs))
        if den_a == 0 or den_b == 0:
            return CorrelationResult(col_a, col_b, None, n)
        r = max(-1.0, min(1.0, num / (den_a * den_b)))
        return CorrelationResult(col_a, col_b, r, n)
