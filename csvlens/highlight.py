"""Utilities for rendering highlighted search matches in terminal output."""

from typing import List, Tuple

ANSI_HIGHLIGHT = "\033[1;33m"  # bold yellow
ANSI_RESET = "\033[0m"


def highlight_spans(
    text: str, spans: List[Tuple[int, int]], highlight: str = ANSI_HIGHLIGHT
) -> str:
    """
    Insert ANSI escape codes around each (start, end) span in *text*.
    Spans must be non-overlapping and sorted by start position.
    """
    if not spans:
        return text

    parts: List[str] = []
    cursor = 0
    for start, end in spans:
        if start > cursor:
            parts.append(text[cursor:start])
        parts.append(f"{highlight}{text[start:end]}{ANSI_RESET}")
        cursor = end
    parts.append(text[cursor:])
    return "".join(parts)


def highlight_cell(value: str, spans: List[Tuple[int, int]]) -> str:
    """Convenience wrapper that applies default highlight colour."""
    return highlight_spans(value, spans)


def strip_ansi(text: str) -> str:
    """Remove all ANSI escape sequences from *text* (useful for tests)."""
    import re
    return re.sub(r"\033\[[0-9;]*m", "", text)
