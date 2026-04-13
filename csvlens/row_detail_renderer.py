"""Renders a single CSV row as a vertical key-value detail view."""

from __future__ import annotations

from typing import List, Optional

ANSI_BOLD = "\033[1m"
ANSI_CYAN = "\033[36m"
ANSI_RESET = "\033[0m"


class RowDetailRenderer:
    """Formats one CSV row as a vertical key-value listing.

    Args:
        headers: Column names for the dataset.
        col_width: Minimum width reserved for the key (header) column.
        colorize: Whether to emit ANSI colour codes.

    Raises:
        ValueError: If *headers* is empty or *col_width* is less than 1.
    """

    def __init__(
        self,
        headers: List[str],
        col_width: int = 20,
        colorize: bool = True,
    ) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        if col_width < 1:
            raise ValueError("col_width must be >= 1")

        self._headers = list(headers)
        self._col_width = col_width
        self._colorize = colorize

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @property
    def col_width(self) -> int:
        return self._col_width

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    def render(self, row: List[str], row_index: Optional[int] = None) -> str:
        """Return a multi-line string showing *row* as key: value pairs.

        Args:
            row: Cell values aligned with *headers*.
            row_index: Optional 0-based row number shown in the header line.

        Raises:
            ValueError: If *row* length does not match *headers* length.
        """
        if len(row) != len(self._headers):
            raise ValueError(
                f"row has {len(row)} columns but headers has {len(self._headers)}"
            )

        lines: List[str] = []

        # Title line
        label = f"Row {row_index}" if row_index is not None else "Row detail"
        if self._colorize:
            lines.append(f"{ANSI_BOLD}{label}{ANSI_RESET}")
        else:
            lines.append(label)

        lines.append("-" * (self._col_width + 3 + 20))

        for header, value in zip(self._headers, row):
            padded_key = header.ljust(self._col_width)
            if self._colorize:
                key_str = f"{ANSI_CYAN}{padded_key}{ANSI_RESET}"
            else:
                key_str = padded_key
            lines.append(f"{key_str} : {value}")

        return "\n".join(lines)
