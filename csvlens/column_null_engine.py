"""Engine that tracks null/empty statistics per column and supports filtering rows by null presence."""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence


class NullSummary:
    """Holds null statistics for a single column."""

    def __init__(self, total: int, null_count: int) -> None:
        self._total = total
        self._null_count = null_count

    @property
    def total(self) -> int:
        return self._total

    @property
    def null_count(self) -> int:
        return self._null_count

    @property
    def non_null_count(self) -> int:
        return self._total - self._null_count

    @property
    def null_rate(self) -> float:
        """Fraction of null values in [0.0, 1.0]."""
        if self._total == 0:
            return 0.0
        return self._null_count / self._total

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"NullSummary(total={self._total}, null_count={self._null_count}, "
            f"null_rate={self.null_rate:.2%})"
        )


class ColumnNullEngine:
    """Computes per-column null statistics and filters rows by null presence."""

    def __init__(self, headers: Sequence[str], rows: Sequence[Dict[str, str]]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._rows: List[Dict[str, str]] = list(rows)
        self._summaries: Dict[str, NullSummary] = self._compute()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def summaries(self) -> Dict[str, NullSummary]:
        return dict(self._summaries)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def summary(self, column: str) -> NullSummary:
        """Return the NullSummary for *column*."""
        if column not in self._summaries:
            raise KeyError(f"Unknown column: {column!r}")
        return self._summaries[column]

    def filter_rows_with_nulls(self, column: str) -> List[Dict[str, str]]:
        """Return only rows where *column* is null/empty."""
        if column not in self._summaries:
            raise KeyError(f"Unknown column: {column!r}")
        return [r for r in self._rows if self._is_null(r.get(column, ""))]

    def filter_rows_without_nulls(self, column: str) -> List[Dict[str, str]]:
        """Return only rows where *column* is non-null/non-empty."""
        if column not in self._summaries:
            raise KeyError(f"Unknown column: {column!r}")
        return [r for r in self._rows if not self._is_null(r.get(column, ""))]

    def columns_above_null_rate(self, threshold: float) -> List[str]:
        """Return column names whose null rate exceeds *threshold*."""
        if not (0.0 <= threshold <= 1.0):
            raise ValueError("threshold must be between 0.0 and 1.0")
        return [col for col, s in self._summaries.items() if s.null_rate > threshold]

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _is_null(value: Optional[str]) -> bool:
        return value is None or value.strip() == ""

    def _compute(self) -> Dict[str, NullSummary]:
        total = len(self._rows)
        result: Dict[str, NullSummary] = {}
        for col in self._headers:
            null_count = sum(1 for r in self._rows if self._is_null(r.get(col, "")))
            result[col] = NullSummary(total=total, null_count=null_count)
        return result
