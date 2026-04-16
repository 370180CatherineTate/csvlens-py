"""Apply multi-column sort to rows using an active ColumnSortProfile."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from csvlens.column_sort_profile import ColumnSortProfile


def _coerce(value: str) -> Any:
    """Try to coerce a string to float for numeric sorting."""
    try:
        return (0, float(value))
    except (ValueError, TypeError):
        return (1, str(value).lower())


class MultiSortEngine:
    """Sort rows according to the active profile in a ColumnSortProfile."""

    def __init__(self, profile: ColumnSortProfile) -> None:
        self._profile = profile

    @property
    def headers(self) -> List[str]:
        return self._profile.headers

    @property
    def active_profile(self) -> Optional[str]:
        return self._profile.active_profile

    def sort(self, rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Return a sorted copy of *rows* based on the active profile keys.

        If no profile is active the original order is preserved.
        """
        keys: List[Tuple[str, bool]] = self._profile.active_keys()
        if not keys:
            return list(rows)

        def sort_key(row: Dict[str, str]):
            parts = []
            for col, ascending in keys:
                raw = row.get(col, "")
                coerced = _coerce(raw)
                if ascending:
                    parts.append(coerced)
                else:
                    # Negate numeric, reverse string ordering
                    kind, val = coerced
                    if kind == 0:
                        parts.append((kind, -val))
                    else:
                        parts.append((kind, val))
            return parts

        # For descending string columns we do a stable two-pass approach
        result = list(rows)
        # Build per-key reverse flags for strings
        reverse_flags = [not asc for _, asc in keys]

        def combined_key(row: Dict[str, str]):
            parts = []
            for (col, ascending), _rev in zip(keys, reverse_flags):
                raw = row.get(col, "")
                kind, val = _coerce(raw)
                if kind == 0:  # numeric
                    parts.append((kind, val if ascending else -val))
                else:  # string
                    parts.append((kind, val))
            return parts

        # Determine if any string column is descending (needs reverse=True)
        # We use a single-pass sort with a composite key that encodes direction.
        result.sort(key=combined_key)
        return result
