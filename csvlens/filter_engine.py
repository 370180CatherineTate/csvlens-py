"""Filter engine for applying regex and column-based filters to CSV rows."""

import re
from typing import List, Dict, Optional, Iterator


class FilterEngine:
    """Applies regex and column-specific filters to CSV data rows."""

    def __init__(self, headers: List[str]):
        self._headers = headers
        self._column_index: Dict[str, int] = {
            col: idx for idx, col in enumerate(headers)
        }
        self._global_pattern: Optional[re.Pattern] = None
        self._column_patterns: Dict[str, re.Pattern] = {}

    def set_global_filter(self, pattern: str, case_sensitive: bool = False) -> None:
        """Set a regex pattern to match against any column value."""
        flags = 0 if case_sensitive else re.IGNORECASE
        self._global_pattern = re.compile(pattern, flags)

    def set_column_filter(self, column: str, pattern: str, case_sensitive: bool = False) -> None:
        """Set a regex pattern for a specific column."""
        if column not in self._column_index:
            raise ValueError(f"Column '{column}' not found in headers: {self._headers}")
        flags = 0 if case_sensitive else re.IGNORECASE
        self._column_patterns[column] = re.compile(pattern, flags)

    def clear_filters(self) -> None:
        """Remove all active filters."""
        self._global_pattern = None
        self._column_patterns.clear()

    def matches(self, row: List[str]) -> bool:
        """Return True if the row passes all active filters."""
        if self._global_pattern:
            if not any(self._global_pattern.search(cell) for cell in row):
                return False

        for column, pattern in self._column_patterns.items():
            idx = self._column_index[column]
            cell = row[idx] if idx < len(row) else ""
            if not pattern.search(cell):
                return False

        return True

    def apply(self, rows: List[List[str]]) -> List[List[str]]:
        """Return a filtered list of rows matching all active filters."""
        return [row for row in rows if self.matches(row)]

    def iter_apply(self, rows: Iterator[List[str]]) -> Iterator[List[str]]:
        """Lazily yield rows that match all active filters."""
        for row in rows:
            if self.matches(row):
                yield row

    @property
    def active_filters(self) -> Dict[str, str]:
        """Return a summary of currently active filters."""
        result = {}
        if self._global_pattern:
            result["__global__"] = self._global_pattern.pattern
        for col, pat in self._column_patterns.items():
            result[col] = pat.pattern
        return result
