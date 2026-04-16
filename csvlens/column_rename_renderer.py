from __future__ import annotations

from csvlens.column_rename_engine import ColumnRenameEngine


class ColumnRenameRenderer:
    """Render a table showing original → display name mappings."""

    def __init__(self, engine: ColumnRenameEngine, col_width: int = 20) -> None:
        if col_width < 4:
            raise ValueError("col_width must be >= 4")
        self._engine = engine
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _pad(self, text: str) -> str:
        text = text[: self._col_width]
        return text.ljust(self._col_width)

    def render(self) -> str:
        renames = self._engine.renames
        if not renames:
            return "(no renames defined)"
        sep = "-" * (self._col_width * 2 + 5)
        header = f"{self._pad('Original')} -> {self._pad('Display')}"
        lines = [header, sep]
        for orig, disp in renames.items():
            lines.append(f"{self._pad(orig)} -> {self._pad(disp)}")
        return "\n".join(lines)

    def render_row(self, row: dict[str, str]) -> dict[str, str]:
        """Return a copy of row keyed by display names."""
        display = self._engine.display_headers()
        original = self._engine.headers
        return {display[i]: row.get(original[i], "") for i in range(len(original))}
