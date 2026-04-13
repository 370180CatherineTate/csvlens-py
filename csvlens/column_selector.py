"""Column selector module for toggling visible columns in the CSV viewer."""

from typing import List, Optional, Set


class ColumnSelector:
    """Manages which columns are currently visible in the viewer."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("Headers list cannot be empty.")
        self._headers = list(headers)
        self._visible: Set[str] = set(headers)

    @property
    def headers(self) -> List[str]:
        """Return all available column headers."""
        return list(self._headers)

    @property
    def visible_headers(self) -> List[str]:
        """Return headers that are currently visible, preserving original order."""
        return [h for h in self._headers if h in self._visible]

    @property
    def hidden_headers(self) -> List[str]:
        """Return headers that are currently hidden."""
        return [h for h in self._headers if h not in self._visible]

    def is_visible(self, column: str) -> bool:
        """Check whether a column is currently visible."""
        return column in self._visible

    def show(self, column: str) -> None:
        """Make a column visible. Raises KeyError if column does not exist."""
        if column not in self._headers:
            raise KeyError(f"Column '{column}' does not exist.")
        self._visible.add(column)

    def hide(self, column: str) -> None:
        """Hide a column. Raises KeyError if column does not exist."""
        if column not in self._headers:
            raise KeyError(f"Column '{column}' does not exist.")
        self._visible.discard(column)

    def toggle(self, column: str) -> bool:
        """Toggle visibility of a column. Returns True if now visible."""
        if column not in self._headers:
            raise KeyError(f"Column '{column}' does not exist.")
        if column in self._visible:
            self._visible.discard(column)
            return False
        else:
            self._visible.add(column)
            return True

    def show_all(self) -> None:
        """Make all columns visible."""
        self._visible = set(self._headers)

    def hide_all(self) -> None:
        """Hide all columns."""
        self._visible.clear()

    def filter_row(self, row: dict) -> dict:
        """Return a filtered dict containing only visible columns."""
        return {k: v for k, v in row.items() if k in self._visible}

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ColumnSelector(total={len(self._headers)}, "
            f"visible={len(self._visible)})"
        )
