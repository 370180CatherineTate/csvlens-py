"""Renders the bookmark list as a formatted text table for the TUI."""

from __future__ import annotations

from typing import List

from csvlens.bookmark_manager import BookmarkManager

_HEADER = ("Name", "Row")
_MIN_NAME_WIDTH = 8
_MIN_ROW_WIDTH = 5


class BookmarkRenderer:
    """Format a :class:`BookmarkManager` into displayable lines."""

    def __init__(self, manager: BookmarkManager) -> None:
        self._manager = manager

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self) -> List[str]:
        """Return a list of strings ready for terminal output.

        Returns an informational message when no bookmarks exist.
        """
        bookmarks = self._manager.all()
        if not bookmarks:
            return ["No bookmarks saved."]

        name_w = max(_MIN_NAME_WIDTH, max(len(n) for n in bookmarks))
        row_w = max(
            _MIN_ROW_WIDTH,
            max(len(str(r)) for r in bookmarks.values()),
        )

        separator = f"+{'-' * (name_w + 2)}+{'-' * (row_w + 2)}+"
        header = (
            f"| {'Name'.ljust(name_w)} | {'Row'.ljust(row_w)} |"
        )

        lines: List[str] = [separator, header, separator]
        for name, row in bookmarks.items():
            lines.append(
                f"| {name.ljust(name_w)} | {str(row).ljust(row_w)} |"
            )
        lines.append(separator)
        return lines

    def render_str(self) -> str:
        """Return rendered output as a single newline-joined string."""
        return "\n".join(self.render())
