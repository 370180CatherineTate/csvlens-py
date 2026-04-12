"""Regex-based search engine for scanning CSV rows and highlighting matches."""

import re
from typing import List, Optional, Tuple


class SearchEngine:
    """Performs regex search across CSV rows, returning match positions."""

    def __init__(self) -> None:
        self._pattern: Optional[re.Pattern] = None
        self._raw_pattern: str = ""

    @property
    def pattern(self) -> str:
        return self._raw_pattern

    def set_pattern(self, pattern: str, case_sensitive: bool = False) -> None:
        """Compile and store a regex pattern for searching."""
        if not pattern:
            self._pattern = None
            self._raw_pattern = ""
            return
        flags = 0 if case_sensitive else re.IGNORECASE
        self._pattern = re.compile(pattern, flags)
        self._raw_pattern = pattern

    def clear(self) -> None:
        """Clear the current search pattern."""
        self._pattern = None
        self._raw_pattern = ""

    def is_active(self) -> bool:
        """Return True if a pattern is currently set."""
        return self._pattern is not None

    def match_row(self, row: dict) -> bool:
        """Return True if any cell in the row matches the pattern."""
        if self._pattern is None:
            return True
        return any(self._pattern.search(str(v)) for v in row.values())

    def find_matches_in_row(
        self, row: dict
    ) -> List[Tuple[str, List[Tuple[int, int]]]]:
        """
        Return a list of (column_name, [(start, end), ...]) for each cell
        that contains at least one match.
        """
        if self._pattern is None:
            return []
        results = []
        for col, val in row.items():
            spans = [
                m.span() for m in self._pattern.finditer(str(val))
            ]
            if spans:
                results.append((col, spans))
        return results

    def filter_rows(
        self, rows: List[dict]
    ) -> List[dict]:
        """Return only the rows that contain at least one match."""
        if self._pattern is None:
            return rows
        return [row for row in rows if self.match_row(row)]
