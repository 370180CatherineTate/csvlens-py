"""Engine that stores per-column regex highlight rules and applies them to cell values."""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple


class ColumnRegexHighlightEngine:
    """Manage per-column regex highlight patterns and produce match spans."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        # column -> compiled pattern
        self._rules: Dict[str, re.Pattern] = {}

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def headers(self) -> List[str]:
        """Return a copy of the header list."""
        return list(self._headers)

    @property
    def rules(self) -> Dict[str, str]:
        """Return a dict of column -> pattern string for active rules."""
        return {col: p.pattern for col, p in self._rules.items()}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def set_rule(self, column: str, pattern: str, *, case_sensitive: bool = False) -> None:
        """Add or update a highlight rule for *column*."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        if not pattern:
            raise ValueError("pattern must not be empty")
        flags = 0 if case_sensitive else re.IGNORECASE
        self._rules[column] = re.compile(pattern, flags)

    def clear_rule(self, column: str) -> None:
        """Remove the highlight rule for *column* (no-op if absent)."""
        self._rules.pop(column, None)

    def clear_all(self) -> None:
        """Remove all highlight rules."""
        self._rules.clear()

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def spans(self, column: str, value: str) -> List[Tuple[int, int]]:
        """Return a list of (start, end) match spans for *value* in *column*.

        Returns an empty list when no rule is set for the column or there
        are no matches.
        """
        pattern = self._rules.get(column)
        if pattern is None:
            return []
        return [(m.start(), m.end()) for m in pattern.finditer(value)]

    def has_rule(self, column: str) -> bool:
        """Return True when an active rule exists for *column*."""
        return column in self._rules
