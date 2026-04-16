from __future__ import annotations
from typing import Dict, List, Set


class ColumnTagEngine:
    """Assign free-form tags to columns and filter columns by tag."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._tags: Dict[str, Set[str]] = {h: set() for h in self._headers}

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def tags(self) -> Dict[str, List[str]]:
        return {h: sorted(self._tags[h]) for h in self._headers}

    def add_tag(self, column: str, tag: str) -> None:
        if column not in self._tags:
            raise KeyError(f"Unknown column: {column!r}")
        tag = tag.strip()
        if not tag:
            raise ValueError("tag must not be blank")
        self._tags[column].add(tag)

    def remove_tag(self, column: str, tag: str) -> None:
        if column not in self._tags:
            raise KeyError(f"Unknown column: {column!r}")
        self._tags[column].discard(tag)

    def clear_tags(self, column: str) -> None:
        if column not in self._tags:
            raise KeyError(f"Unknown column: {column!r}")
        self._tags[column].clear()

    def columns_with_tag(self, tag: str) -> List[str]:
        return [h for h in self._headers if tag in self._tags[h]]

    def all_tags(self) -> List[str]:
        result: Set[str] = set()
        for s in self._tags.values():
            result |= s
        return sorted(result)
