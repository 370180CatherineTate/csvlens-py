"""Engine for assigning display colors to columns by name or pattern."""
from __future__ import annotations
import re
from typing import Dict, List, Optional

_VALID_COLORS = {"red", "green", "yellow", "blue", "magenta", "cyan", "white"}

_ANSI = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37mclass ColumnColorEngine:
    """ foreground colors to columns; patternbased rules are supported."""

    def __init__(self, not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._exact: Dict[str, str] = {}      # column -> color
        self._patterns: List[tuple[str, str]] = []  # (regex, color)

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    def set_color(self, column: str, color: str) -> None:
        """Assign *color* to an exact column name."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        color = color.lower()
        if color not in _VALID_COLORS:
            raise ValueError(f"Invalid color {color!r}. Choose from {sorted(_VALID_COLORS)}")
        self._exact[column] = color

    def set_pattern_color(self, pattern: str, color: str) -> None:
        """Assign *color* to all columns whose name matches *pattern* (regex)."""
        color = color.lower()
        if color not in _VALID_COLORS:
            raise ValueError(f"Invalid color {color!r}. Choose from {sorted(_VALID_COLORS)}")
        re.compile(pattern)  # validate early
        self._patterns.append((pattern, color))

    def clear_color(self, column: str) -> None:
        """Remove any explicit color for *column*."""
        self._exact.pop(column, None)

    def clear_all(self) -> None:
        self._exact.clear()
        self._patterns.clear()

    def color_for(self, column: str) -> Optional[str]:
        """Return the resolved color name for *column*, or None."""
        if column in self._exact:
            return self._exact[column]
        for pattern, color in reversed(self._patterns):
            if re.search(pattern, column):
                return color
        return None

    def ansi_for(self, column: str) -> str:
        """Return the ANSI escape code for *column*, or empty string."""
        c = self.color_for(column)
        return _ANSI.get(c, "") if c else ""

    def colorize(self, column: str, text: str) -> str:
        """Wrap the ANSI color assigned to *column*."""
        code = self.ansi_for(column)
        if not code:
            return text
        return f"{code}{text}{_ANSI['reset']}"
