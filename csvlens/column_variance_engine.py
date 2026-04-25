from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Dict, List, Optional


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


@dataclass
class VarianceResult:
    column: str
    count: int
    numeric_count: int
    variance: Optional[float]
    std_dev: Optional[float]
    mean: Optional[float]
    cv: Optional[float]  # coefficient of variation

    def summary(self) -> str:
        if self.variance is None:
            return f"{self.column}: no numeric data"
        cv_str = f", CV={self.cv:.3f}" if self.cv is not None else ""
        return (
            f"{self.column}: var={self.variance:.4f}, "
            f"std={self.std_dev:.4f}, mean={self.mean:.4f}{cv_str}"
        )


class ColumnVarianceEngine:
    """Computes variance, standard deviation, mean, and CV for numeric columns."""

    def __init__(self, headers: List[str], rows: List[Dict[str, str]]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers = list(headers)
        self._rows = rows
        self._results: Dict[str, VarianceResult] = self._compute()

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def results(self) -> Dict[str, VarianceResult]:
        return dict(self._results)

    def get(self, column: str) -> VarianceResult:
        if column not in self._results:
            raise KeyError(f"Unknown column: {column!r}")
        return self._results[column]

    def _compute(self) -> Dict[str, VarianceResult]:
        out: Dict[str, VarianceResult] = {}
        for col in self._headers:
            values = [
                _to_float(row.get(col, ""))
                for row in self._rows
            ]
            numeric = [v for v in values if v is not None]
            n = len(numeric)
            if n < 2:
                out[col] = VarianceResult(
                    column=col,
                    count=len(self._rows),
                    numeric_count=n,
                    variance=None,
                    std_dev=None,
                    mean=numeric[0] if n == 1 else None,
                    cv=None,
                )
            else:
                var = statistics.variance(numeric)
                std = math.sqrt(var)
                mean = statistics.mean(numeric)
                cv = (std / mean) if mean != 0 else None
                out[col] = VarianceResult(
                    column=col,
                    count=len(self._rows),
                    numeric_count=n,
                    variance=var,
                    std_dev=std,
                    mean=mean,
                    cv=cv,
                )
        return out
