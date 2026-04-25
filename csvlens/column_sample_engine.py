from __future__ import annotations

import random
from typing import Dict, List, Optional


class SampleResult:
    """Holds a random sample of values for a single column."""

    def __init__(self, column: str, values: List[str], seed: Optional[int]) -> None:
        self._column = column
        self._values = list(values)
        self._seed = seed

    @property
    def column(self) -> str:
        return self._column

    @property
    def values(self) -> List[str]:
        return list(self._values)

    @property
    def seed(self) -> Optional[int]:
        return self._seed

    @property
    def count(self) -> int:
        return len(self._values)

    def summary(self) -> str:
        preview = ", ".join(self._values[:3])
        if len(self._values) > 3:
            preview += ", ..."
        return f"{self._column}: [{preview}] ({self.count} samples)"


class ColumnSampleEngine:
    """Randomly samples values from each column in a dataset."""

    def __init__(
        self,
        headers: List[str],
        rows: List[Dict[str, str]],
        sample_size: int = 5,
        seed: Optional[int] = None,
    ) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        if sample_size < 1:
            raise ValueError("sample_size must be at least 1")

        self._headers = list(headers)
        self._rows = rows
        self._sample_size = sample_size
        self._seed = seed
        self._results: Dict[str, SampleResult] = {}
        self._compute()

    def _compute(self) -> None:
        rng = random.Random(self._seed)
        for col in self._headers:
            values = [row.get(col, "") for row in self._rows]
            k = min(self._sample_size, len(values))
            sampled = rng.sample(values, k) if k > 0 else []
            self._results[col] = SampleResult(col, sampled, self._seed)

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def sample_size(self) -> int:
        return self._sample_size

    @property
    def results(self) -> Dict[str, SampleResult]:
        return dict(self._results)

    def get(self, column: str) -> SampleResult:
        if column not in self._results:
            raise KeyError(f"Unknown column: {column!r}")
        return self._results[column]

    def resample(self, seed: Optional[int] = None) -> None:
        """Re-run sampling with an optional new seed."""
        self._seed = seed
        self._compute()
