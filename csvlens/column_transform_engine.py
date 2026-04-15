"""Engine for applying per-column value transformations (e.g. upper, lower, strip, truncate)."""

from typing import Callable, Dict, List, Optional

_BUILTIN_TRANSFORMS: Dict[str, Callable[[str], str]] = {
    "upper": str.upper,
    "lower": str.lower,
    "strip": str.strip,
    "title": str.title,
}


class ColumnTransformEngine:
    """Applies named or custom transforms to column values at render time."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._transforms: Dict[str, Callable[[str], str]] = {}

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def transforms(self) -> Dict[str, str]:
        """Return a mapping of column -> transform name (builtins only) or '<custom>'."""
        result = {}
        for col, fn in self._transforms.items():
            name = next((k for k, v in _BUILTIN_TRANSFORMS.items() if v is fn), "<custom>")
            result[col] = name
        return result

    def set_transform(self, column: str, transform: str) -> None:
        """Assign a builtin transform name to a column."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        if transform not in _BUILTIN_TRANSFORMS:
            raise ValueError(
                f"Unknown transform {transform!r}. "
                f"Available: {list(_BUILTIN_TRANSFORMS)}"
            )
        self._transforms[column] = _BUILTIN_TRANSFORMS[transform]

    def set_custom_transform(self, column: str, fn: Callable[[str], str]) -> None:
        """Assign an arbitrary callable as a transform for a column."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        if not callable(fn):
            raise TypeError("fn must be callable")
        self._transforms[column] = fn

    def clear_transform(self, column: str) -> None:
        """Remove any transform for the given column."""
        self._transforms.pop(column, None)

    def clear_all(self) -> None:
        """Remove all transforms."""
        self._transforms.clear()

    def apply_row(self, row: Dict[str, str]) -> Dict[str, str]:
        """Return a new row dict with transforms applied to matching columns."""
        result = {}
        for col, value in row.items():
            fn = self._transforms.get(col)
            result[col] = fn(value) if fn is not None else value
        return result

    def apply_rows(self, rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Apply transforms to every row in the list."""
        return [self.apply_row(r) for r in rows]
