from __future__ import annotations

from typing import Dict, List, Optional


class ColumnRatingEngine:
    """Assign 1-5 star ratings to columns and query them."""

    MIN_RATING = 1
    MAX_RATING = 5

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._ratings: Dict[str, int] = {}

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def ratings(self) -> Dict[str, int]:
        return dict(self._ratings)

    def set_rating(self, column: str, rating: int) -> None:
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        if not (self.MIN_RATING <= rating <= self.MAX_RATING):
            raise ValueError(
                f"rating must be between {self.MIN_RATING} and {self.MAX_RATING}, got {rating}"
            )
        self._ratings[column] = rating

    def clear_rating(self, column: str) -> None:
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        self._ratings.pop(column, None)

    def get_rating(self, column: str) -> Optional[int]:
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        return self._ratings.get(column)

    def columns_with_min_rating(self, min_rating: int) -> List[str]:
        return [c for c, r in self._ratings.items() if r >= min_rating]

    def clear_all(self) -> None:
        self._ratings.clear()
