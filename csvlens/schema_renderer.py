"""Renders a SchemaInspector result as a formatted table string."""

from __future__ import annotations

from typing import List, Optional

from csvlens.schema_inspector import SchemaInspector

_TYPE_COLORS: dict = {
    "integer": "\033[34m",   # blue
    "float":   "\033[36m",   # cyan
    "boolean": "\033[33m",   # yellow
    "date":    "\033[32m",   # green
    "string":  "\033[0m",    # default
    "null":    "\033[90m",   # dark grey
}
_RESET = "\033[0m"


class SchemaRenderer:
    """Formats schema information into a human-readable table."""

    def __init__(
        self,
        inspector: SchemaInspector,
        use_color: bool = True,
        col_width: int = 20,
    ) -> None:
        if col_width < 4:
            raise ValueError("col_width must be >= 4")
        self._inspector = inspector
        self._use_color = use_color
        self._col_width = col_width

    def _colorize(self, text: str, type_name: str) -> str:
        if not self._use_color:
            return text
        color = _TYPE_COLORS.get(type_name, "")
        return f"{color}{text}{_RESET}"

    def _pad(self, text: str) -> str:
        return text[: self._col_width].ljust(self._col_width)

    def render(self) -> str:
        schema = self._inspector.schema
        header_line = self._pad("COLUMN") + "  " + self._pad("TYPE")
        sep = "-" * len(header_line)
        lines: List[str] = [header_line, sep]
        for col in self._inspector.headers:
            type_name = schema.get(col, "string")
            col_cell = self._pad(col)
            type_cell = self._colorize(self._pad(type_name), type_name)
            lines.append(f"{col_cell}  {type_cell}")
        return "\n".join(lines)

    def render_str(self) -> str:
        """Alias for render(); returns plain string."""
        return self.render()
