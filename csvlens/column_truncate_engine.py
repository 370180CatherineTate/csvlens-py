"""Engine for truncating long cell values with configurable max length and ellipsis."""

from __future__ import annotations


class ColumnTruncateEngine:
    """Truncates cell values to a maximum character length per column."""

    _ELLIPSIS = "..."
    _MIN_MAX_LEN = 4  # must fit at least one char + ellipsis

    def __init__(self, headers: list[str], default_max_len: int = 30) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        if default_max_len < self._MIN_MAX_LEN:
            raise ValueError(
                f"default_max_len must be >= {self._MIN_MAX_LEN}, got {default_max_len}"
            )
        self._headers: list[str] = list(headers)
        self._default_max_len = default_max_len
        self._overrides: dict[str, int] = {}

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def headers(self) -> list[str]:
        return list(self._headers)

    @property
    def default_max_len(self) -> int:
        return self._default_max_len

    @property
    def overrides(self) -> dict[str, int]:
        return dict(self._overrides)

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_override(self, column: str, max_len: int) -> None:
        """Set a per-column max length override."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        if max_len < self._MIN_MAX_LEN:
            raise ValueError(
                f"max_len must be >= {self._MIN_MAX_LEN}, got {max_len}"
            )
        self._overrides[column] = max_len

    def clear_override(self, column: str) -> None:
        """Remove a per-column override, reverting to default."""
        self._overrides.pop(column, None)

    def clear_all_overrides(self) -> None:
        """Remove all per-column overrides."""
        self._overrides.clear()

    # ------------------------------------------------------------------
    # Truncation
    # ------------------------------------------------------------------

    def max_len_for(self, column: str) -> int:
        """Return the effective max length for a given column."""
        return self._overrides.get(column, self._default_max_len)

    def truncate(self, column: str, value: str) -> str:
        """Truncate *value* for *column* if it exceeds the max length."""
        max_len = self.max_len_for(column)
        if len(value) <= max_len:
            return value
        return value[: max_len - len(self._ELLIPSIS)] + self._ELLIPSIS

    def truncate_row(self, row: dict[str, str]) -> dict[str, str]:
        """Return a new dict with all values truncated to their column limits."""
        return {col: self.truncate(col, val) for col, val in row.items() if col in self._headers}
