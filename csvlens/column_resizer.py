"""ColumnResizer: manage per-column display widths with min/max constraints."""

from __future__ import annotations

_DEFAULT_MIN = 4
_DEFAULT_MAX = 40
_DEFAULT_WIDTH = 12


class ColumnResizer:
    """Tracks and adjusts display widths for each column."""

    def __init__(
        self,
        headers: list[str],
        min_width: int = _DEFAULT_MIN,
        max_width: int = _DEFAULT_MAX,
        default_width: int = _DEFAULT_WIDTH,
    ) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        if min_width < 1:
            raise ValueError("min_width must be >= 1")
        if max_width < min_width:
            raise ValueError("max_width must be >= min_width")
        if not (min_width <= default_width <= max_width):
            raise ValueError("default_width must be between min_width and max_width")

        self._headers = list(headers)
        self._min = min_width
        self._max = max_width
        self._widths: dict[str, int] = {h: default_width for h in self._headers}

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def headers(self) -> list[str]:
        return list(self._headers)

    @property
    def min_width(self) -> int:
        return self._min

    @property
    def max_width(self) -> int:
        return self._max

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_width(self, column: str) -> int:
        """Return the current display width for *column*."""
        if column not in self._widths:
            raise KeyError(f"Unknown column: {column!r}")
        return self._widths[column]

    def set_width(self, column: str, width: int) -> None:
        """Set an explicit width for *column*, clamped to [min, max]."""
        if column not in self._widths:
            raise KeyError(f"Unknown column: {column!r}")
        self._widths[column] = max(self._min, min(self._max, width))

    def widen(self, column: str, step: int = 2) -> int:
        """Increase width by *step* and return the new value."""
        if step < 1:
            raise ValueError("step must be >= 1")
        self.set_width(column, self._widths[column] + step)
        return self._widths[column]

    def narrow(self, column: str, step: int = 2) -> int:
        """Decrease width by *step* and return the new value."""
        if step < 1:
            raise ValueError("step must be >= 1")
        self.set_width(column, self._widths[column] - step)
        return self._widths[column]

    def auto_fit(self, column: str, rows: list[dict[str, str]]) -> int:
        """Fit width to the longest value (or header) seen in *rows*."""
        if column not in self._widths:
            raise KeyError(f"Unknown column: {column!r}")
        best = len(column)
        for row in rows:
            val = row.get(column, "")
            if val and len(val) > best:
                best = len(val)
        self.set_width(column, best)
        return self._widths[column]

    def all_widths(self) -> dict[str, int]:
        """Return a snapshot of all column widths."""
        return dict(self._widths)

    def reset(self, default_width: int | None = None) -> None:
        """Reset all columns to *default_width* (or the original default)."""
        dw = default_width if default_width is not None else _DEFAULT_WIDTH
        dw = max(self._min, min(self._max, dw))
        for h in self._headers:
            self._widths[h] = dw
