"""Persist and switch between named multi-column sort configurations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SortProfile:
    """A named, ordered list of (column, ascending) sort keys."""

    name: str
    keys: List[Tuple[str, bool]] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.keys) == 0

    def description(self) -> str:
        if self.is_empty():
            return f"{self.name}: (empty)"
        parts = [f"{col} {'ASC' if asc else 'DESC'}" for col, asc in self.keys]
        return f"{self.name}: " + ", ".join(parts)


class ColumnSortProfile:
    """Manage multiple named sort profiles for a set of headers."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._profiles: Dict[str, SortProfile] = {}
        self._active: Optional[str] = None

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def profile_names(self) -> List[str]:
        return list(self._profiles.keys())

    @property
    def active_profile(self) -> Optional[str]:
        return self._active

    def save(self, name: str, keys: List[Tuple[str, bool]]) -> None:
        """Save a sort profile. Validates all columns exist."""
        if not name:
            raise ValueError("profile name must not be empty")
        for col, _ in keys:
            if col not in self._headers:
                raise KeyError(f"column '{col}' not in headers")
        self._profiles[name] = SortProfile(name=name, keys=list(keys))

    def activate(self, name: str) -> SortProfile:
        """Set the active profile and return it."""
        if name not in self._profiles:
            raise KeyError(f"profile '{name}' does not exist")
        self._active = name
        return self._profiles[name]

    def deactivate(self) -> None:
        """Clear the active profile."""
        self._active = None

    def get(self, name: str) -> SortProfile:
        if name not in self._profiles:
            raise KeyError(f"profile '{name}' does not exist")
        return self._profiles[name]

    def delete(self, name: str) -> None:
        if name not in self._profiles:
            raise KeyError(f"profile '{name}' does not exist")
        if self._active == name:
            self._active = None
        del self._profiles[name]

    def active_keys(self) -> List[Tuple[str, bool]]:
        """Return the sort keys of the active profile, or [] if none active."""
        if self._active is None:
            return []
        return list(self._profiles[self._active].keys)
