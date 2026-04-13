"""DiffEngine: compare two sets of rows and report added, removed, and changed rows."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple


@dataclass
class DiffResult:
    added: List[Dict[str, str]] = field(default_factory=list)
    removed: List[Dict[str, str]] = field(default_factory=list)
    changed: List[Tuple[Dict[str, str], Dict[str, str]]] = field(default_factory=list)

    @property
    def has_diff(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    @property
    def summary(self) -> Dict[str, int]:
        return {
            "added": len(self.added),
            "removed": len(self.removed),
            "changed": len(self.changed),
        }


class DiffEngine:
    """Compare two lists of row dicts keyed by a primary-key column."""

    def __init__(
        self,
        headers: Sequence[str],
        key_column: Optional[str] = None,
    ) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers = list(headers)
        self._key_column = key_column or self._headers[0]
        if self._key_column not in self._headers:
            raise ValueError(f"key_column '{self._key_column}' not found in headers")

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def key_column(self) -> str:
        return self._key_column

    def compute(self
        , baseline: Sequence[Dict[str, str]]
        , current: Sequence[Dict[str, str]]
    ) -> DiffResult:
        """Return a DiffResult comparing *baseline* rows against *current* rows."""
        base_map: Dict[str, Dict[str, str]] = {
            row[self._key_column]: row for row in baseline
        }
        curr_map: Dict[str, Dict[str, str]] = {
            row[self._key_column]: row for row in current
        }

        result = DiffResult()
        for key, row in curr_map.items():
            if key not in base_map:
                result.added.append(row)
            elif row != base_map[key]:
                result.changed.append((base_map[key], row))

        for key, row in base_map.items():
            if key not in curr_map:
                result.removed.append(row)

        return result
