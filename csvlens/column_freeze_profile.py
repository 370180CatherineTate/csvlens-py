"""Persist and restore named freeze configurations for columns."""
from __future__ import annotations
from typing import Dict, List, Optional


class ColumnFreezeProfile:
    """Store named freeze profiles (sets of frozen column names)."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._profiles: Dict[str, List[str]] = {}
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

    def save(self, name: str, frozen: List[str]) -> None:
        """Save a freeze profile by name."""
        if not name or not name.strip():
            raise ValueError("profile name must not be empty")
        invalid = [c for c in frozen if c not in self._headers]
        if invalid:
            raise ValueError(f"unknown columns: {invalid}")
        self._profiles[name] = list(frozen)

    def activate(self, name: str) -> List[str]:
        """Activate a profile and return its frozen column list."""
        if name not in self._profiles:
            raise KeyError(f"profile '{name}' not found")
        self._active = name
        return list(self._profiles[name])

    def deactivate(self) -> None:
        """Clear the active profile."""
        self._active = None

    def delete(self, name: str) -> None:
        """Remove a saved profile."""
        if name not in self._profiles:
            raise KeyError(f"profile '{name}' not found")
        if self._active == name:
            self._active = None
        del self._profiles[name]

    def get(self, name: str) -> List[str]:
        """Return frozen columns for a named profile."""
        if name not in self._profiles:
            raise KeyError(f"profile '{name}' not found")
        return list(self._profiles[name])
