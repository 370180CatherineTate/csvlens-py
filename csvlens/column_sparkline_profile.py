"""Persist and switch named sparkline configurations across columns."""

from __future__ import annotations

from typing import Dict, List, Optional


class ColumnSparklineProfile:
    """Store named sparkline width profiles and apply them to a column set.

    Each profile maps column names to a spark_width (int).  Only columns
    present in *headers* are accepted.

    Parameters
    ----------
    headers:
        Ordered list of column names in the CSV.

    Raises
    ------
    ValueError
        If *headers* is empty.
    """

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        # profile_name -> {column -> spark_width}
        self._profiles: Dict[str, Dict[str, int]] = {}
        self._active: Optional[str] = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def headers(self) -> List[str]:
        """Return a copy of the column headers."""
        return list(self._headers)

    @property
    def profile_names(self) -> List[str]:
        """Return saved profile names in insertion order."""
        return list(self._profiles.keys())

    @property
    def active_profile(self) -> Optional[str]:
        """Return the name of the currently active profile, or *None*."""
        return self._active

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def save(self, name: str, widths: Dict[str, int]) -> None:
        """Save a profile.

        Parameters
        ----------
        name:
            Arbitrary label for the profile.
        widths:
            Mapping of column name to spark_width.  Unknown columns are
            silently ignored.  Values must be >= 1.

        Raises
        ------
        ValueError
            If any provided spark_width is less than 1.
        """
        if not name:
            raise ValueError("profile name must not be empty")
        filtered: Dict[str, int] = {}
        for col, w in widths.items():
            if col not in self._headers:
                continue
            if w < 1:
                raise ValueError(
                    f"spark_width for '{col}' must be >= 1, got {w}"
                )
            filtered[col] = w
        self._profiles[name] = filtered

    def activate(self, name: str) -> None:
        """Set *name* as the active profile.

        Raises
        ------
        KeyError
            If *name* does not exist.
        """
        if name not in self._profiles:
            raise KeyError(f"profile '{name}' not found")
        self._active = name

    def deactivate(self) -> None:
        """Clear the active profile (no sparkline overrides applied)."""
        self._active = None

    def delete(self, name: str) -> None:
        """Remove a saved profile.

        Raises
        ------
        KeyError
            If *name* does not exist.
        """
        if name not in self._profiles:
            raise KeyError(f"profile '{name}' not found")
        del self._profiles[name]
        if self._active == name:
            self._active = None

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get_widths(self) -> Dict[str, int]:
        """Return the width mapping for the active profile.

        Returns an empty dict when no profile is active.
        """
        if self._active is None:
            return {}
        return dict(self._profiles[self._active])

    def get_width(self, column: str, default: int = 8) -> int:
        """Return the spark_width for *column* under the active profile.

        Falls back to *default* when no profile is active or the column
        is not listed in the active profile.
        """
        widths = self.get_widths()
        return widths.get(column, default)
