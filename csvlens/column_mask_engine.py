"""Engine for masking (redacting) column values with a placeholder string."""
from __future__ import annotations

from typing import Dict, List


class ColumnMaskEngine:
    """Tracks which columns are masked and applies redaction to rows."""

    DEFAULT_MASK = "***"

    def __init__(self, headers: List[str], default_mask: str = DEFAULT_MASK) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._default_mask = default_mask
        self._masks: Dict[str, str] = {}  # col -> mask string

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def masked_columns(self) -> List[str]:
        """Return columns that are currently masked."""
        return list(self._masks.keys())

    @property
    def default_mask(self) -> str:
        return self._default_mask

    def mask(self, column: str, placeholder: str | None = None) -> None:
        """Mask *column* with *placeholder* (or the default mask)."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        self._masks[column] = placeholder if placeholder is not None else self._default_mask

    def unmask(self, column: str) -> None:
        """Remove masking from *column*."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        self._masks.pop(column, None)

    def clear(self) -> None:
        """Remove all masks."""
        self._masks.clear()

    def is_masked(self, column: str) -> bool:
        return column in self._masks

    def apply(self, row: Dict[str, str]) -> Dict[str, str]:
        """Return a copy of *row* with masked columns replaced by their placeholder."""
        result = dict(row)
        for col, placeholder in self._masks.items():
            if col in result:
                result[col] = placeholder
        return result

    def apply_rows(self, rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Apply masking to every row in *rows*."""
        return [self.apply(r) for r in rows]
