"""Compute simple linear trend (slope direction) for numeric columns."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


@dataclass
class TrendResult:
    column: str
    count: int          # number of numeric values used
    slope: float        # positive → rising, negative → falling, 0 → flat
    direction: str      # 'up', 'down', or 'flat'

    @property
    def summary(self) -> str:
        arrow = {"up": "↑", "down": "↓", "flat": "→"}[self.direction]
        return f"{arrow} slope={self.slope:+.4f} (n={self.count})"


class ColumnTrendEngine:
    """Compute per-column linear trend over row order for a set of rows."""

    def __init__(self, headers: Sequence[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._results: Dict[str, TrendResult] = {}

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def results(self) -> Dict[str, TrendResult]:
        return dict(self._results)

    def compute(self, rows: Sequence[Dict[str, str]]) -> None:
        """Compute trends for all headers given the provided rows."""
        self._results.clear()
        for col in self._headers:
            values: List[float] = []
            for row in rows:
                v = _to_float(row.get(col, ""))
                if v is not None:
                    values.append(v)
            self._results[col] = self._trend(col, values)

    @staticmethod
    def _trend(col: str, values: List[float]) -> TrendResult:
        n = len(values)
        if n < 2:
            return TrendResult(column=col, count=n, slope=0.0, direction="flat")
        xs = list(range(n))
        mean_x = sum(xs) / n
        mean_y = sum(values) / n
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, values))
        den = sum((x - mean_x) ** 2 for x in xs)
        slope = num / den if den != 0 else 0.0
        if slope > 1e-9:
            direction = "up"
        elif slope < -1e-9:
            direction = "down"
        else:
            direction = "flat"
        return TrendResult(column=col, count=n, slope=slope, direction=direction)

    def get(self, column: str) -> TrendResult:
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        if column not in self._results:
            return TrendResult(column=column, count=0, slope=0.0, direction="flat")
        return self._results[column]
