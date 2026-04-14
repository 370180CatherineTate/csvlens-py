"""Manages named visibility profiles for column sets."""
from __future__ import annotations

from typing import Dict, List, Optional


class ColumnVisibilityProfile:
    """Store and switch between named column visibility profiles.

    A profile is a named snapshot of which columns are visible.
    Profiles can be saved, loaded, and deleted by name.
    """

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._profiles: Dict[str, List[str]] = {}
        self._active: Optional[str] = None

    @property
    def headers(self) -> List[str]:
        """Return the full list of column headers."""
        return list(self._headers)

    @property
    def profile_names(self) -> List[str]:
        """Return sorted list of saved profile names."""
        return sorted(self._profiles.keys())

    @property
    def active_profile(self) -> Optional[str]:
        """Return the name of the currently active profile, or None."""
        return self._active

    def save(self, name: str, visible: List[str]) -> None:
        """Save a visibility profile under *name*.

        Args:
            name: Non-empty profile name.
            visible: List of header names that should be visible.
                     All entries must be known headers.

        Raises:
            ValueError: If *name* is empty or any column in *visible* is unknown.
        """
        if not name:
            raise ValueError("profile name must not be empty")
        unknown = [c for c in visible if c not in self._headers]
        if unknown:
            raise ValueError(f"unknown columns: {unknown}")
        self._profiles[name] = list(visible)

    def load(self, name: str) -> List[str]:
        """Activate a profile and return its visible column list.

        Raises:
            KeyError: If *name* does not exist.
        """
        if name not in self._profiles:
            raise KeyError(f"profile '{name}' not found")
        self._active = name
        return list(self._profiles[name])

    def delete(self, name: str) -> None:
        """Remove a saved profile.

        Raises:
            KeyError: If *name* does not exist.
        """
        if name not in self._profiles:
            raise KeyError(f"profile '{name}' not found")
        del self._profiles[name]
        if self._active == name:
            self._active = None

    def get(self, name: str) -> Optional[List[str]]:
        """Return the visible columns for *name*, or None if not found."""
        return list(self._profiles[name]) if name in self._profiles else None
