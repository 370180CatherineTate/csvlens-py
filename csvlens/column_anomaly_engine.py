"""Detects anomalous values in columns using IQR-based outlier detection."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _to_float(val: str) -> Optional[float]:
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


@dataclass
class AnomalyResult:
    column: str
    total: int
    anomaly_count: int
    anomaly_indices: List[int] = field(default_factory=list)
    q1: Optional[float] = None
    q3: Optional[float] = None
    iqr: Optional[float] = None

    @property
    def anomaly_pct(self) -> float:
        if self.total == 0:
            return 0.0
        return round(self.anomaly_count / self.total * 100, 2)

    @property
    def summary(self) -> str:
        if self.iqr is None:
            return f"{self.column}: no numeric data"
        return (
            f"{self.column}: {self.anomaly_count}/{self.total} anomalies "
            f"({self.anomaly_pct}%) | IQR=[{self.q1},{self.q3}]"
        )


class ColumnAnomalyEngine:
    def __init__(self, headers: List[str], rows: List[Dict[str, str]], multiplier: float = 1.5) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        if multiplier <= 0:
            raise ValueError("multiplier must be positive")
        self._headers = list(headers)
        self._rows = rows
        self._multiplier = multiplier
        self._results: Dict[str, AnomalyResult] = {}
        self._compute()

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def multiplier(self) -> float:
        return self._multiplier

    @property
    def results(self) -> Dict[str, AnomalyResult]:
        return dict(self._results)

    def get(self, column: str) -> AnomalyResult:
        if column not in self._results:
            raise KeyError(f"Unknown column: {column!r}")
        return self._results[column]

    def _compute(self) -> None:
        for col in self._headers:
            values = [_to_float(r.get(col, "")) for r in self._rows]
            numeric = sorted(v for v in values if v is not None)
            total = len(self._rows)
            if len(numeric) < 4:
                self._results[col] = AnomalyResult(col, total, 0)
                continue
            n = len(numeric)
            q1 = numeric[n // 4]
            q3 = numeric[(3 * n) // 4]
            iqr = q3 - q1
            lo = q1 - self._multiplier * iqr
            hi = q3 + self._multiplier * iqr
            anomaly_indices = [
                i for i, v in enumerate(values) if v is not None and (v < lo or v > hi)
            ]
            self._results[col] = AnomalyResult(
                col, total, len(anomaly_indices), anomaly_indices,
                round(q1, 4), round(q3, 4), round(iqr, 4)
            )
