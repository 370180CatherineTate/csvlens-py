"""Engine for assigning and resolving display aliases for CSV column headers."""

from __future__ import annotations

from typing import Dict, List, Optional


class ColumnAliasEngine:
    """Manages user-defined display aliases for column headers."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must be a non-empty list")
        self._headers: List[str] = list(headers)
        self._aliases: Dict[str, str] = {}

    @property
    def headers(self) -> List[str]:
        """Return the original column headers."""
        return list(self._headers)

    @property
    def aliases(self) -> Dict[str, str]:
        """Return a copy of the current alias mapping (original -> alias)."""
        return dict(self._aliases)

    def set_alias(self, column: str, alias: str) -> None:
        """Assign a display alias to a column.

        Args:
            column: The original column name.
            alias: The alias to display instead.

        Raises:
            KeyError: If *column* is not a known header.
            ValueError: If *alias* is empty or already used by another column.
        """
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        alias = alias.strip()
        if not alias:
            raise ValueError("alias must be a non-empty string")
        for orig, existing in self._aliases.items():
            if existing == alias and orig != column:
                raise ValueError(
                    f"alias {alias!r} is already assigned to column {orig!r}"
                )
        self._aliases[column] = alias

    def remove_alias(self, column: str) -> None:
        """Remove the alias for *column*, reverting to the original name."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        self._aliases.pop(column, None)

    def clear_aliases(self) -> None:
        """Remove all aliases."""
        self._aliases.clear()

    def display_name(self, column: str) -> str:
        """Return the display name (alias if set, otherwise original)."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        return self._aliases.get(column, column)

    def display_headers(self) -> List[str]:
        """Return the full list of headers using aliases where defined."""
        return [self._aliases.get(h, h) for h in self._headers]

    def resolve(self, display_name: str) -> Optional[str]:
        """Resolve a display name back to the original column name.

        Returns *None* if no match is found.
        """
        for orig in self._headers:
            if self._aliases.get(orig, orig) == display_name:
                return orig
        return None
