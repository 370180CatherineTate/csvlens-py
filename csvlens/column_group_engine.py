"""Engine for grouping and collapsing multiple columns under a named group label."""

from __future__ import annotations
from typing import Dict, List, Optional


class ColumnGroupEngine:
    """Manages named groups of columns that can be collapsed/expanded."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._groups: Dict[str, List[str]] = {}   # group_name -> [col, ...]
        self._collapsed: set = set()               # group names currently collapsed

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def groups(self) -> Dict[str, List[str]]:
        return {k: list(v) for k, v in self._groups.items()}

    @property
    def group_names(self) -> List[str]:
        return list(self._groups.keys())

    def add_group(self, name: str, columns: List[str]) -> None:
        """Create a named group from a list of existing column names."""
        if not name or not name.strip():
            raise ValueError("group name must be a non-empty string")
        if not columns:
            raise ValueError("columns list must not be empty")
        unknown = [c for c in columns if c not in self._headers]
        if unknown:
            raise ValueError(f"unknown columns: {unknown}")
        self._groups[name] = list(columns)

    def remove_group(self, name: str) -> None:
        """Delete a group (does not affect underlying columns)."""
        if name not in self._groups:
            raise KeyError(f"group '{name}' does not exist")
        self._groups.pop(name)
        self._collapsed.discard(name)

    def collapse(self, name: str) -> None:
        """Mark a group as collapsed so only its label is shown."""
        if name not in self._groups:
            raise KeyError(f"group '{name}' does not exist")
        self._collapsed.add(name)

    def expand(self, name: str) -> None:
        """Mark a group as expanded (default state)."""
        if name not in self._groups:
            raise KeyError(f"group '{name}' does not exist")
        self._collapsed.discard(name)

    def is_collapsed(self, name: str) -> bool:
        return name in self._collapsed

    def visible_headers(self) -> List[str]:
        """Return the effective header list respecting collapsed groups.

        Collapsed group columns are replaced by a single '[GroupName]' placeholder.
        """
        hidden: set = set()
        placeholders: Dict[str, str] = {}  # first col in group -> placeholder label
        for gname in self._collapsed:
            cols = self._groups[gname]
            placeholders[cols[0]] = f"[{gname}]"
            hidden.update(cols[1:])

        result: List[str] = []
        for h in self._headers:
            if h in hidden:
                continue
            if h in placeholders:
                result.append(placeholders[h])
            else:
                result.append(h)
        return result

    def group_for_column(self, column: str) -> Optional[str]:
        """Return the group name that owns *column*, or None."""
        for gname, cols in self._groups.items():
            if column in cols:
                return gname
        return None
