"""Renders the filter history stack as a formatted string for display."""

from csvlens.row_filter_history import RowFilterHistory

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_HIGHLIGHT = "\033[7m"  # reverse video


class FilterHistoryRenderer:
    """Produces a multi-line string showing the filter history.

    The active (current) entry is highlighted; past entries are dimmed;
    future (redo) entries are shown in normal style.
    """

    def __init__(self, history: RowFilterHistory, col_width: int = 60) -> None:
        if col_width < 10:
            raise ValueError("col_width must be at least 10")
        self._history = history
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _pad(self, text: str) -> str:
        return text[: self._col_width].ljust(self._col_width)

    def render(self, use_color: bool = True) -> str:
        stack = self._history._stack
        cursor = self._history._cursor

        if not stack:
            msg = self._pad(" No filter history.")
            return f"{_DIM}{msg}{_RESET}" if use_color else msg

        lines: list[str] = []
        header = self._pad(f" Filter History ({len(stack)} entries)")
        if use_color:
            lines.append(f"{_BOLD}{header}{_RESET}")
        else:
            lines.append(header)

        for idx, snapshot in enumerate(stack):
            prefix = "  "
            if idx == cursor:
                prefix = "► "
            elif idx < cursor:
                prefix = "  "
            else:
                prefix = "  "

            desc = snapshot.description()
            label = self._pad(f"{prefix}[{idx}] {desc}")

            if use_color:
                if idx == cursor:
                    lines.append(f"{_HIGHLIGHT}{label}{_RESET}")
                elif idx < cursor:
                    lines.append(f"{_DIM}{label}{_RESET}")
                else:
                    lines.append(label)
            else:
                lines.append(label)

        undo_str = "undo:available" if self._history.can_undo else "undo:none"
        redo_str = "redo:available" if self._history.can_redo else "redo:none"
        footer = self._pad(f" [{undo_str}]  [{redo_str}]")
        if use_color:
            lines.append(f"{_DIM}{footer}{_RESET}")
        else:
            lines.append(footer)

        return "\n".join(lines)

    def render_str(self) -> str:
        """Convenience wrapper — returns plain text without ANSI codes."""
        return self.render(use_color=False)
