"""Engine for computing unique value counts per column."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class UniqueResult:
    """Unique-value statistics for a single column."""

    column: str
    total: int
    unique_count: int
    sample_values: List[str]

    @property
    def uniqueness_ratio(self) -> float:
        """Fraction of rows that have a distinct value (0.0 – 1.0)."""
        if self.total == 0:
            return 0.0
        return self.unique_count / self.total

    @property
    def is_key_candidate(self) -> bool:
        """True when every non-null value is unique."""
        return self.unique_count == self.total and self.total > 0

    def summary(self) -> str:
        ratio_pct = f"{self.uniqueness_ratio * 100:.1f}%"
        return (
            f"{self.column}: {self.unique_count}/{self.total} unique "
            f"({ratio_pct})"
        )


class ColumnUniqueEngine:
    """Compute unique-value statistics for each column in a dataset."""

    def __init__(
        self,
        headers: List[str],
        rows: List[Dict[str, str]],
        *,
        sample_size: int = 5,
    ) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        if sample_size < 1:
            raise ValueError("sample_size must be at least 1")

        self._headers: List[str] = list(headers)
        self._sample_size = sample_size
        self._results: Dict[str, UniqueResult] = self._compute(rows)

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def results(self) -> Dict[str, UniqueResult]:
        return dict(self._results)

    def get(self, column: str) -> UniqueResult:
        if column not in self._results:
            raise KeyError(f"Unknown column: {column!r}")
        return self._results[column]

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _compute(self, rows: List[Dict[str, str]]) -> Dict[str, UniqueResult]:
        results: Dict[str, UniqueResult] = {}
        for col in self._headers:
            seen: dict[str, int] = {}
            for row in rows:
                val = row.get(col, "") or ""
                seen[val] = seen.get(val, 0) + 1
            unique_vals = sorted(seen.keys())
            sample = unique_vals[: self._sample_size]
            results[col] = UniqueResult(
                column=col,
                total=len(rows),
                unique_count=len(seen),
                sample_values=sample,
            )
        return results
