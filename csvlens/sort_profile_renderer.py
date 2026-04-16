"""Render a ColumnSortProfile summary for display in the TUI."""
from __future__ import annotations

from typing import List

from csvlens.column_sort_profile import ColumnSortProfile

_ANSI_BOLD = "\033[1m"
_ANSI_DIM = "\033[2m"
_ANSI_RESET = "\033[0m"
_ANSI_GREEN = "\033[32m"
_ANSI_YELLOW = "\033[33m"


class SortProfileRenderer:
    """Render sort profile information as a formatted string block."""

    def __init__(self, profile: ColumnSortProfile, col_width: int = 30) -> None:
        if col_width < 8:
            raise ValueError("col_width must be >= 8")
        self._profile = profile
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _pad(self, text: str) -> str:
        return text[: self._col_width].ljust(self._col_width)

    def render(self) -> str:
        lines: List[str] = []
        header = _ANSI_BOLD + self._pad("Sort Profiles") + _ANSI_RESET
        lines.append(header)
        lines.append("-" * self._col_width)

        if not self._profile.profile_names:
            lines.append(_ANSI_DIM + self._pad("(no profiles saved)") + _ANSI_RESET)
        else:
            for name in self._profile.profile_names:
                sp = self._profile.get(name)
                marker = (
                    _ANSI_GREEN + "* " + _ANSI_RESET
                    if name == self._profile.active_profile
                    else "  "
                )
                label = marker + _ANSI_YELLOW + name + _ANSI_RESET
                lines.append(label)
                desc = sp.description()
                # indent the description
                for part in desc.split(": ", 1)[1:]:
                    lines.append("    " + self._pad(part))

        lines.append("-" * self._col_width)
        active_keys = self._profile.active_keys()
        if active_keys:
            active_name = self._profile.active_profile
            lines.append(f"Active: {active_name}")
        else:
            lines.append(_ANSI_DIM + "Active: (none)" + _ANSI_RESET)

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.render()
