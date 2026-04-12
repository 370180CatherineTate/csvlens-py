"""Shared mutable search state consumed by the viewer and renderer."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SearchState:
    """Holds the current search pattern and per-row match metadata."""

    pattern: str = ""
    case_sensitive: bool = False
    # Maps row_index -> {col_name: [(start, end), ...]}
    match_map: Dict[int, Dict[str, List[Tuple[int, int]]]] = field(
        default_factory=dict
    )
    matched_row_indices: List[int] = field(default_factory=list)

    # Index into matched_row_indices for cycling through results
    _cursor: int = 0

    def reset(self) -> None:
        """Clear all search state."""
        self.pattern = ""
        self.match_map.clear()
        self.matched_row_indices.clear()
        self._cursor = 0

    @property
    def total_matches(self) -> int:
        return len(self.matched_row_indices)

    def current_match_row(self) -> Optional[int]:
        """Return the row index of the currently focused match."""
        if not self.matched_row_indices:
            return None
        return self.matched_row_indices[self._cursor % len(self.matched_row_indices)]

    def next_match(self) -> Optional[int]:
        """Advance cursor and return the next matched row index."""
        if not self.matched_row_indices:
            return None
        self._cursor = (self._cursor + 1) % len(self.matched_row_indices)
        return self.current_match_row()

    def prev_match(self) -> Optional[int]:
        """Move cursor back and return the previous matched row index."""
        if not self.matched_row_indices:
            return None
        self._cursor = (self._cursor - 1) % len(self.matched_row_indices)
        return self.current_match_row()
