"""Column statistics computation for CSV data."""

from collections import Counter
from typing import Any


class ColumnStats:
    """Computes and stores statistics for a single CSV column."""

    def __init__(self, name: str, values: list[str]) -> None:
        self.name = name
        self._values = values
        self._numeric: list[float] = []
        self._non_empty: list[str] = []
        self._compute()

    def _compute(self) -> None:
        for v in self._values:
            stripped = v.strip()
            if stripped:
                self._non_empty.append(stripped)
                try:
                    self._numeric.append(float(stripped))
                except ValueError:
                    pass

    @property
    def total_count(self) -> int:
        return len(self._values)

    @property
    def null_count(self) -> int:
        return self.total_count - len(self._non_empty)

    @property
    def unique_count(self) -> int:
        return len(set(self._non_empty))

    @property
    def is_numeric(self) -> bool:
        return len(self._numeric) == len(self._non_empty) and len(self._non_empty) > 0

    @property
    def min_value(self) -> float | str | None:
        if self.is_numeric:
            return min(self._numeric) if self._numeric else None
        return min(self._non_empty) if self._non_empty else None

    @property
    def max_value(self) -> float | str | None:
        if self.is_numeric:
            return max(self._numeric) if self._numeric else None
        return max(self._non_empty) if self._non_empty else None

    @property
    def mean(self) -> float | None:
        if self.is_numeric and self._numeric:
            return sum(self._numeric) / len(self._numeric)
        return None

    @property
    def top_values(self) -> list[tuple[str, int]]:
        counter = Counter(self._non_empty)
        return counter.most_common(5)

    def summary(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": self.name,
            "total": self.total_count,
            "nulls": self.null_count,
            "unique": self.unique_count,
            "is_numeric": self.is_numeric,
            "min": self.min_value,
            "max": self.max_value,
            "top_values": self.top_values,
        }
        if self.is_numeric:
            result["mean"] = round(self.mean, 4) if self.mean is not None else None
        return result
