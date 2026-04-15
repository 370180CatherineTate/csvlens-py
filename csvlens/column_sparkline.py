"""Render a compact sparkline bar chart for numeric column distributions."""
from __future__ import annotations

from typing import List, Optional

_BLOCKS = " ▁▂▃▄▅▆▇█"


def _to_buckets(values: List[float], n_buckets: int) -> List[int]:
    """Distribute *values* into *n_buckets* equal-width buckets; return counts."""
    if not values:
        return [0] * n_buckets
    lo, hi = min(values), max(values)
    span = hi - lo
    counts = [0] * n_buckets
    for v in values:
        if span == 0:
            idx = 0
        else:
            idx = int((v - lo) / span * (n_buckets - 1))
        counts[idx] += 1
    return counts


class ColumnSparkline:
    """Generate a text sparkline for a named numeric column."""

    def __init__(self, headers: List[str], rows: List[dict]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers = list(headers)
        self._rows = rows

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    def _numeric_values(self, column: str) -> List[float]:
        """Return all finite float values for *column*, skipping blanks."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        result: List[float] = []
        for row in self._rows:
            raw = row.get(column, "")
            if raw is None or str(raw).strip() == "":
                continue
            try:
                result.append(float(raw))
            except (ValueError, TypeError):
                pass
        return result

    def render(self, column: str, width: int = 10) -> str:
        """Return a sparkline string of *width* characters for *column*."""
        if width < 1:
            raise ValueError("width must be >= 1")
        values = self._numeric_values(column)
        if not values:
            return "-" * width
        counts = _to_buckets(values, width)
        max_count = max(counts) or 1
        chars = []
        for c in counts:
            level = int(c / max_count * (len(_BLOCKS) - 1))
            chars.append(_BLOCKS[level])
        return "".join(chars)

    def render_labeled(self, column: str, width: int = 10) -> str:
        """Return '<column>: <sparkline>' labelled string."""
        return f"{column}: {self.render(column, width)}"
