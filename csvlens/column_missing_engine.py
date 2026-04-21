"""Engine for analysing missing-value patterns across columns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence


@dataclass
class MissingSummary:
    """Missing-value statistics for a single column."""

    column: str
    total: int
    missing: int

    @property
    def present(self) -> int:
        return self.total - self.missing

    @property
    def missing_pct(self) -> float:
        if self.total == 0:
            return 0.0
        return round(self.missing / self.total * 100, 2)

    @property
    def present_pct(self) -> float:
        return round(100.0 - self.missing_pct, 2)

    def summary(self) -> Dict[str, object]:
        return {
            "column": self.column,
            "total": self.total,
            "missing": self.missing,
            "present": self.present,
            "missing_pct": self.missing_pct,
            "present_pct": self.present_pct,
        }


class ColumnMissingEngine:
    """Compute missing-value statistics for each column in *rows*."""

    def __init__(
        self,
        headers: Sequence[str],
        rows: Sequence[Dict[str, str]],
        *,
        null_values: Optional[Sequence[str]] = None,
    ) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._rows = rows
        self._null_values: frozenset[str] = frozenset(
            null_values if null_values is not None else ("", "null", "NULL", "NA", "N/A", "none", "None")
        )
        self._summaries: Dict[str, MissingSummary] = self._compute()

    # ------------------------------------------------------------------
    # public
    # ------------------------------------------------------------------

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def summaries(self) -> Dict[str, MissingSummary]:
        return dict(self._summaries)

    def get(self, column: str) -> MissingSummary:
        if column not in self._summaries:
            raise KeyError(f"Unknown column: {column!r}")
        return self._summaries[column]

    def most_missing(self) -> Optional[str]:
        """Return the column name with the highest missing count, or None."""
        if not self._summaries:
            return None
        return max(self._summaries, key=lambda c: self._summaries[c].missing)

    # ------------------------------------------------------------------
    # internal
    # ------------------------------------------------------------------

    def _compute(self) -> Dict[str, MissingSummary]:
        counts: Dict[str, int] = {h: 0 for h in self._headers}
        total = len(self._rows)
        for row in self._rows:
            for h in self._headers:
                val = row.get(h, "")
                if val is None or str(val).strip() in self._null_values:
                    counts[h] += 1
        return {
            h: MissingSummary(column=h, total=total, missing=counts[h])
            for h in self._headers
        }
