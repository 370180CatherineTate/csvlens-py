"""DiffRenderer: produce a human-readable coloured summary of a DiffResult."""
from __future__ import annotations

from typing import List

from csvlens.diff_engine import DiffResult

_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_RESET = "\033[0m"
_BOLD = "\033[1m"


class DiffRenderer:
    def __init__(self, col_width: int = 20, use_color: bool = True) -> None:
        if col_width < 4:
            raise ValueError("col_width must be >= 4")
        self._col_width = col_width
        self._use_color = use_color

    def _c(self, code: str, text: str) -> str:
        if not self._use_color:
            return text
        return f"{code}{text}{_RESET}"

    def _pad(self, value: str) -> str:
        value = str(value)
        if len(value) > self._col_width:
            value = value[: self._col_width - 1] + "…"
        return value.ljust(self._col_width)

    def render(self, result: DiffResult) -> str:
        lines: List[str] = []
        summary = result.summary
        lines.append(
            self._c(_BOLD, f"Diff summary — "
                f"+{summary['added']} added  "
                f"-{summary['removed']} removed  "
                f"~{summary['changed']} changed")
        )
        for row in result.added:
            lines.append(self._c(_GREEN, "+ " + "  ".join(self._pad(v) for v in row.values())))
        for row in result.removed:
            lines.append(self._c(_RED, "- " + "  ".join(self._pad(v) for v in row.values())))
        for old, new in result.changed:
            lines.append(self._c(_YELLOW, "~ OLD: " + "  ".join(self._pad(v) for v in old.values())))
            lines.append(self._c(_YELLOW, "  NEW: " + "  ".join(self._pad(v) for v in new.values())))
        return "\n".join(lines)

    def render_str(self, result: DiffResult) -> str:  # alias
        return self.render(result)
