from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


@dataclass
class OutlierResult:
    column: str
    mean: float
    std: float
    outlier_indices: List[int]

    @property
    def count(self) -> int:
        return len(self.outlier_indices)


class ColumnOutlierEngine:
    """Detects outliers in numeric columns using z-score threshold."""

    def __init__(self, headers: List[str], z_threshold: float = 2.0) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        if z_threshold <= 0:
            raise ValueError("z_threshold must be positive")
        self._headers = list(headers)
        self._z_threshold = z_threshold
        self._results: Dict[str, OutlierResult] = {}

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def z_threshold(self) -> float:
        return self._z_threshold

    def analyse(self, rows: List[Dict[str, str]]) -> None:
        """Run outlier detection across all numeric columns."""
        self._results = {}
        for col in self._headers:
            pairs = [(i, _to_float(r.get(col, ""))) for i, r in enumerate(rows)]
            numeric = [(i, v) for i, v in pairs if v is not None]
            if len(numeric) < 2:
                continue
            values = [v for _, v in numeric]
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            std = variance ** 0.5
            if std == 0:
                continue
            outliers = [i for i, v in numeric if abs(v - mean) / std > self._z_threshold]
            self._results[col] = OutlierResult(column=col, mean=mean, std=std, outlier_indices=outliers)

    def result_for(self, column: str) -> Optional[OutlierResult]:
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        return self._results.get(column)

    def outlier_columns(self) -> List[str]:
        """Return columns that have at least one outlier."""
        return [col for col, r in self._results.items() if r.count > 0]
