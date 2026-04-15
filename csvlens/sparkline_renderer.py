"""Render a table of sparklines for all numeric columns."""
from __future__ import annotations

from typing import List

from csvlens.column_sparkline import ColumnSparkline

_ANSI_CYAN = "\033[36m"
_ANSI_RESET = "\033[0m"


class SparklineRenderer:
    """Render a multi-row display of per-column sparklines."""

    def __init__(
        self,
        sparkline: ColumnSparkline,
        col_width: int = 20,
        spark_width: int = 12,
    ) -> None:
        if col_width < 4:
            raise ValueError("col_width must be >= 4")
        if spark_width < 1:
            raise ValueError("spark_width must be >= 1")
        self._spark = sparkline
        self._col_width = col_width
        self._spark_width = spark_width

    @property
    def col_width(self) -> int:
        return self._col_width

    @property
    def spark_width(self) -> int:
        return self._spark_width

    def _pad(self, text: str, width: int) -> str:
        return text[:width].ljust(width)

    def render(self, columns: List[str] | None = None) -> str:
        """Return a formatted string with one sparkline row per column."""
        targets = columns if columns is not None else self._spark.headers
        lines: List[str] = []
        header = self._pad("Column", self._col_width) + "  Distribution"
        lines.append(header)
        lines.append("-" * (self._col_width + 2 + self._spark_width))
        for col in targets:
            try:
                spark = self._spark.render(col, self._spark_width)
            except KeyError:
                spark = "?" * self._spark_width
            label = _ANSI_CYAN + self._pad(col, self._col_width) + _ANSI_RESET
            lines.append(f"{label}  {spark}")
        return "\n".join(lines)
