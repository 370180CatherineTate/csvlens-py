"""Sort engine for ordering CSV rows by a given column."""

from typing import List, Dict, Optional


class SortEngine:
    """Sorts rows by a specified column, ascending or descending."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers = headers
        self._sort_column: Optional[str] = None
        self._ascending: bool = True

    @property
    def sort_column(self) -> Optional[str]:
        """Currently active sort column, or None if unsorted."""
        return self._sort_column

    @property
    def ascending(self) -> bool:
        """True if sorting ascending, False if descending."""
        return self._ascending

    def set_sort(self, column: str, ascending: bool = True) -> None:
        """Set the column to sort by and direction."""
        if column not in self._headers:
            raise KeyError(f"Column '{column}' not found in headers")
        self._sort_column = column
        self._ascending = ascending

    def clear_sort(self) -> None:
        """Remove any active sort, returning to natural order."""
        self._sort_column = None
        self._ascending = True

    def sort(self, rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Return a sorted copy of *rows*.

        Numeric values are sorted numerically; anything else is sorted
        lexicographically.  Blank / non-numeric values sort last.
        """
        if self._sort_column is None:
            return list(rows)

        col = self._sort_column

        def sort_key(row: Dict[str, str]):
            val = row.get(col, "")
            try:
                return (0, float(val))
            except (ValueError, TypeError):
                if val == "" or val is None:
                    return (2, val)
                return (1, val.lower())

        return sorted(rows, key=sort_key, reverse=not self._ascending)
