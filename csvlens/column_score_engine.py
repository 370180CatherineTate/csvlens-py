from __future__ import annotations

from typing import Dict, List, Optional


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


class ColumnScoreEngine:
    """Compute a weighted composite score for each row across numeric columns."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers = list(headers)
        self._weights: Dict[str, float] = {}

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def weights(self) -> Dict[str, float]:
        return dict(self._weights)

    def set_weight(self, column: str, weight: float) -> None:
        if column not in self._headers:
            raise KeyError(f"column {column!r} not in headers")
        if weight < 0:
            raise ValueError("weight must be >= 0")
        self._weights[column] = weight

    def clear_weight(self, column: str) -> None:
        self._weights.pop(column, None)

    def clear_all(self) -> None:
        self._weights.clear()

    def score_row(self, row: Dict[str, str]) -> Optional[float]:
        """Return weighted sum for *row*; None if no weights are configured."""
        if not self._weights:
            return None
        total = 0.0
        for col, w in self._weights.items():
            val = _to_float(row.get(col, ""))
            if val is not None:
                total += val * w
        return total

    def score_rows(self, rows: List[Dict[str, str]]) -> List[Optional[float]]:
        return [self.score_row(r) for r in rows]

    def ranked(self, rows: List[Dict[str, str]], ascending: bool = False) -> List[Dict[str, str]]:
        """Return *rows* sorted by composite score (highest first by default)."""
        scored = [(self.score_row(r), r) for r in rows]
        scored.sort(key=lambda t: (t[0] is None, t[0] if t[0] is not None else 0), reverse=not ascending)
        return [r for _, r in scored]
