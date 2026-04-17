from __future__ import annotations
from typing import Dict, List, Optional


class ColumnIndexEngine:
    """Builds and queries an in-memory index mapping column values to row indices."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        # column -> value -> sorted list of row indices
        self._index: Dict[str, Dict[str, List[int]]] = {}

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def indexed_columns(self) -> List[str]:
        return list(self._index.keys())

    def build(self, column: str, rows: List[Dict[str, str]]) -> None:
        """Index all values for *column* across *rows*."""
        if column not in self._headers:
            raise KeyError(f"column '{column}' not in headers")
        mapping: Dict[str, List[int]] = {}
        for i, row in enumerate(rows):
            val = row.get(column, "")
            mapping.setdefault(val, []).append(i)
        self._index[column] = mapping

    def lookup(self, column: str, value: str) -> List[int]:
        """Return row indices where *column* == *value*."""
        if column not in self._index:
            raise KeyError(f"column '{column}' has not been indexed")
        return list(self._index[column].get(value, []))

    def unique_values(self, column: str) -> List[str]:
        """Return sorted unique values for an indexed column."""
        if column not in self._index:
            raise KeyError(f"column '{column}' has not been indexed")
        return sorted(self._index[column].keys())

    def drop(self, column: str) -> None:
        """Remove the index for *column* if present."""
        self._index.pop(column, None)

    def clear(self) -> None:
        """Remove all indexes."""
        self._index.clear()
