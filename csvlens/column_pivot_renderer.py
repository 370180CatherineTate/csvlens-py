from __future__ import annotations
from typing import Dict
from csvlens.column_pivot_engine import ColumnPivotEngine


class ColumnPivotRenderer:
    """Render pivot results as a simple text table."""

    def __init__(self, engine: ColumnPivotEngine, col_width: int = 16) -> None:
        if col_width < 4:
            raise ValueError("col_width must be >= 4")
        self._engine = engine
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _pad(self, text: str) -> str:
        text = str(text)
        if len(text) > self._col_width:
            text = text[: self._col_width - 1] + "…"
        return text.ljust(self._col_width)

    def render(self, pivot_result: Dict[str, float]) -> str:
        key_col = self._engine.key_column or "key"
        val_col = self._engine.value_column or "value"
        agg = self._engine.agg
        header = self._pad(key_col) + "  " + self._pad(f"{val_col} ({agg})")
        sep = "-" * len(header)
        lines = [header, sep]
        for key in sorted(pivot_result):
            val = pivot_result[key]
            fmt_val = f"{val:.2f}" if val != int(val) else str(int(val))
            lines.append(self._pad(key) + "  " + self._pad(fmt_val))
        if not pivot_result:
            lines.append(self._pad("(no data)"))
        return "\n".join(lines)
