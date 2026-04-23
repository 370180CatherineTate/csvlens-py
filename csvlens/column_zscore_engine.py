from __future__ import annotations

import math
from typing import Dict, List, Optional


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


class ZScoreResult:
    """Z-score statistics for a single column."""

    def __init__(self, column: str, scores: List[Optional[float]]) -> None:
        self._column = column
        self._scores = scores

    @property
    def column(self) -> str:
        return self._column

    @property
    def scores(self) -> List[Optional[float]]:
        return list(self._scores)

    @property
    def outlier_count(self) -> int:
        """Number of rows with |z| > 3."""
        return sum(1 for s in self._scores if s is not None and abs(s) > 3.0)

    def summary(self) -> str:
        valid = [s for s in self._scores if s is not None]
        if not valid:
            return f"{self._column}: no numeric data"
        max_z = max(abs(s) for s in valid)
        return (
            f"{self._column}: n={len(valid)}, "
            f"outliers={self.outlier_count}, max|z|={max_z:.2f}"
        )


class ColumnZScoreEngine:
    """Compute per-column z-scores across a dataset."""

    def __init__(self, headers: List[str], rows: List[Dict[str, str]]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers = list(headers)
        self._results: Dict[str, ZScoreResult] = {}
        self._compute(rows)

    def _compute(self, rows: List[Dict[str, str]]) -> None:
        for col in self._headers:
            raw = [_to_float(row.get(col, "")) for row in rows]
            valid = [v for v in raw if v is not None]
            if len(valid) < 2:
                scores: List[Optional[float]] = [None] * len(raw)
            else:
                mean = sum(valid) / len(valid)
                variance = sum((v - mean) ** 2 for v in valid) / len(valid)
                std = math.sqrt(variance) if variance > 0 else 0.0
                scores = [
                    ((v - mean) / std) if (v is not None and std > 0) else None
                    for v in raw
                ]
            self._results[col] = ZScoreResult(col, scores)

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def results(self) -> Dict[str, ZScoreResult]:
        return dict(self._results)

    def get(self, column: str) -> ZScoreResult:
        if column not in self._results:
            raise KeyError(f"Unknown column: {column!r}")
        return self._results[column]
