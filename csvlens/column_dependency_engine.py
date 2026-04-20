"""Track inter-column dependencies (e.g. derived / correlated columns)."""
from __future__ import annotations

from typing import Dict, List, Set


class ColumnDependencyEngine:
    """Record which columns depend on other columns.

    A *dependency* means column A is derived from (or logically requires)
    one or more other columns.  The engine lets callers query transitive
    dependents and ancestors so the UI can highlight related columns.
    """

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        # maps column -> set of columns it directly depends on
        self._deps: Dict[str, Set[str]] = {h: set() for h in self._headers}

    # ------------------------------------------------------------------
    # properties
    # ------------------------------------------------------------------

    @property
    def headers(self) -> List[str]:
        """Return a copy of the original header list."""
        return list(self._headers)

    @property
    def dependencies(self) -> Dict[str, List[str]]:
        """Return a snapshot of all direct dependencies."""
        return {col: sorted(deps) for col, deps in self._deps.items()}

    # ------------------------------------------------------------------
    # mutation
    # ------------------------------------------------------------------

    def add_dependency(self, column: str, depends_on: str) -> None:
        """Declare that *column* directly depends on *depends_on*."""
        for name in (column, depends_on):
            if name not in self._deps:
                raise KeyError(f"Unknown column: {name!r}")
        if column == depends_on:
            raise ValueError("A column cannot depend on itself")
        self._deps[column].add(depends_on)

    def remove_dependency(self, column: str, depends_on: str) -> None:
        """Remove a previously declared direct dependency (no-op if absent)."""
        if column not in self._deps:
            raise KeyError(f"Unknown column: {column!r}")
        self._deps[column].discard(depends_on)

    def clear_dependencies(self, column: str) -> None:
        """Remove all direct dependencies for *column*."""
        if column not in self._deps:
            raise KeyError(f"Unknown column: {column!r}")
        self._deps[column].clear()

    # ------------------------------------------------------------------
    # queries
    # ------------------------------------------------------------------

    def direct_dependencies(self, column: str) -> List[str]:
        """Return columns that *column* directly depends on."""
        if column not in self._deps:
            raise KeyError(f"Unknown column: {column!r}")
        return sorted(self._deps[column])

    def transitive_dependencies(self, column: str) -> List[str]:
        """Return all columns that *column* transitively depends on."""
        if column not in self._deps:
            raise KeyError(f"Unknown column: {column!r}")
        visited: Set[str] = set()
        stack = list(self._deps[column])
        while stack:
            cur = stack.pop()
            if cur in visited:
                continue
            visited.add(cur)
            stack.extend(self._deps.get(cur, set()))
        return sorted(visited)

    def dependents(self, column: str) -> List[str]:
        """Return columns that directly depend on *column*."""
        if column not in self._deps:
            raise KeyError(f"Unknown column: {column!r}")
        return sorted(c for c, deps in self._deps.items() if column in deps)
