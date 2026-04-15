"""Persist and restore named color profiles for ColumnColorEngine."""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

from csvlens.column_color_engine import ColumnColorEngine


class ColumnColorProfile:
    """Store named snapshots of color assignments and restore them on demand."""

    def __init__(self, engine: ColumnColorEngine) -> None:
        self._engine = engine
        # profile_name -> (exact dict, patterns list)
        self._profiles: Dict[str, Tuple[Dict[str, str], List[Tuple[str, str]]]] = {}
        self._active: Optional[str] = None

    @property
    def profile_names(self) -> List[str]:
        return list(self._profiles.keys())

    @property
    def active_profile(self) -> Optional[str]:
        return self._active

    def save(self, name: str) -> None:
        """Snapshot the engine's current colors under *name*."""
        if not name or not name.strip():
            raise ValueError("Profile name must not be blank")
        exact = dict(self._engine._(self._engine._patterns)
        self._profiles[name] = (exact, patterns)

    def load(self, name: str) -> None:
        """Restore the color state saved under *name*."""
        if name not in self._profiles:
            raise KeyError(f"No profile named {name!r}")
        exact, patterns = self._profiles[name]
        self._engine.clear_all()
        for col, color in exact.items():
            self._engine._exact[col] = color
        for pattern, color in patterns:
            self._engine._patterns.append((pattern, color))
        self._active = name

    def delete(self, name: str) -> None:
        """Remove a saved profile."""
        if name not in self._profiles:
            raise KeyError(f"No profile named {name!r}")
        del self._profiles[name]
        if self._active == name:
            self._active = None

    def reset_active(self) -> None:
        """Clear the active profile marker without changing colors."""
        self._active = None
