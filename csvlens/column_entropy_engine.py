"""Compute Shannon entropy for each column to measure value diversity."""
from __future__ import annotations

import math
from collections import Counter
from typing import Dict, List, Optional


class EntropyResult:
    """Holds entropy statistics for a single column."""

    def __init__(self, column: str, entropy: Optional[float], unique: int, total: int) -> None:
        self._column = column
        self._entropy = entropy
        self._unique = unique
        self._total = total

    @property
    def column(self) -> str:
        return self._column

    @property
    def entropy(self) -> Optional[float]:
        """Shannon entropy in bits; None when total == 0."""
        return self._entropy

    @property
    def unique(self) -> int:
        return self._unique

    @property
    def total(self) -> int:
        return self._total

    @property
    def normalised(self) -> Optional[float]:
        """Entropy divided by log2(unique) so it falls in [0, 1]; None when unique < 2."""
        if self._entropy is None or self._unique < 2:
            return None
        return self._entropy / math.log2(self._unique)


class ColumnEntropyEngine:
    """Compute Shannon entropy for every column in a dataset."""

    def __init__(self, headers: List[str], rows: List[Dict[str, str]]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers = list(headers)
        self._results: Dict[str, EntropyResult] = {}
        self._compute(rows)

    def _compute(self, rows: List[Dict[str, str]]) -> None:
        for col in self._headers:
            values = [r.get(col, "") for r in rows]
            total = len(values)
            if total == 0:
                self._results[col] = EntropyResult(col, None, 0, 0)
                continue
            counts = Counter(values)
            unique = len(counts)
            entropy = 0.0
            for cnt in counts.values():
                p = cnt / total
                entropy -= p * math.log2(p)
            self._results[col] = EntropyResult(col, round(entropy, 6), unique, total)

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def results(self) -> Dict[str, EntropyResult]:
        return dict(self._results)

    def get(self, column: str) -> EntropyResult:
        if column not in self._results:
            raise KeyError(f"Unknown column: {column!r}")
        return self._results[column]

    def ranked(self, descending: bool = True) -> List[EntropyResult]:
        """Return results sorted by entropy value."""
        valid = [r for r in self._results.values() if r.entropy is not None]
        return sorted(valid, key=lambda r: r.entropy, reverse=descending)  # type: ignore[arg-type]
