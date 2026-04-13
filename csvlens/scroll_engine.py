"""ScrollEngine: manages vertical and horizontal scroll offsets for the CSV viewer."""


class ScrollEngine:
    """Tracks and updates scroll position within a paginated CSV view."""

    def __init__(self, total_rows: int, total_cols: int, page_size: int = 20, col_window: int = 5):
        if total_rows < 0:
            raise ValueError("total_rows must be non-negative")
        if total_cols <= 0:
            raise ValueError("total_cols must be positive")
        if page_size <= 0:
            raise ValueError("page_size must be positive")
        if col_window <= 0:
            raise ValueError("col_window must be positive")

        self._total_rows = total_rows
        self._total_cols = total_cols
        self._page_size = page_size
        self._col_window = col_window
        self._row_offset = 0
        self._col_offset = 0

    @property
    def row_offset(self) -> int:
        return self._row_offset

    @property
    def col_offset(self) -> int:
        return self._col_offset

    @property
    def max_row_offset(self) -> int:
        return max(0, self._total_rows - self._page_size)

    @property
    def max_col_offset(self) -> int:
        return max(0, self._total_cols - self._col_window)

    def scroll_down(self, lines: int = 1) -> None:
        """Scroll down by *lines* rows, clamped to the last valid offset."""
        self._row_offset = min(self._row_offset + lines, self.max_row_offset)

    def scroll_up(self, lines: int = 1) -> None:
        """Scroll up by *lines* rows, clamped to zero."""
        self._row_offset = max(self._row_offset - lines, 0)

    def scroll_right(self, cols: int = 1) -> None:
        """Scroll right by *cols* columns, clamped to the last valid offset."""
        self._col_offset = min(self._col_offset + cols, self.max_col_offset)

    def scroll_left(self, cols: int = 1) -> None:
        """Scroll left by *cols* columns, clamped to zero."""
        self._col_offset = max(self._col_offset - cols, 0)

    def jump_to_row(self, row: int) -> None:
        """Set row offset directly, clamped to valid range."""
        self._row_offset = max(0, min(row, self.max_row_offset))

    def reset(self) -> None:
        """Reset both offsets to the origin."""
        self._row_offset = 0
        self._col_offset = 0

    def visible_row_slice(self) -> slice:
        """Return a slice for the currently visible row window."""
        return slice(self._row_offset, self._row_offset + self._page_size)

    def visible_col_slice(self) -> slice:
        """Return a slice for the currently visible column window."""
        return slice(self._col_offset, self._col_offset + self._col_window)
