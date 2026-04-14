"""Renders a compact single-line summary bar for a specific column."""

from __future__ import annotations

from typing import Any, Dict, List

from csvlens.column_stats import ColumnStats


class ColumnSummaryBar:
    """Produces a concise one-line summary string for a column.

    The bar format is:
        <name>  type:<type>  non-null:<n>  null:<n>  unique:<n>  [min:<v>  max:<v>  mean:<v>]
    Numeric extras are only appended when the column contains numeric data.
    """

    _ANSI_BOLD = "\033[1m"
    _ANSI_CYAN = "\033[36m"
    _ANSI_RESET = "\033[0m"

    def __init__(self, headers: List[str], rows: List[Dict[str, Any]], col_width: int = 14) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        if col_width < 4:
            raise ValueError("col_width must be >= 4")

        self._headers = list(headers)
        self._rows = rows
        self._col_width = col_width
        self._stats: Dict[str, ColumnStats] = {
            h: ColumnStats(h, rows) for h in self._headers
        }

    # ------------------------------------------------------------------
    # public
    # ------------------------------------------------------------------

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    def render(self, column: str, *, color: bool = True) -> str:
        """Return a single-line summary bar string for *column*."""
        if column not in self._stats:
            raise KeyError(f"Unknown column: {column!r}")

        st = self._stats[column]
        summary = st.summary()

        parts: List[str] = [
            self._fmt_label("col", column, color),
            self._fmt_kv("type", summary.get("type", "?"), color),
            self._fmt_kv("non-null", str(summary.get("non_null_count", 0)), color),
            self._fmt_kv("null", str(summary.get("null_count", 0)), color),
            self._fmt_kv("unique", str(summary.get("unique_count", 0)), color),
        ]

        if summary.get("type") == "numeric":
            for key in ("min", "max", "mean"):
                val = summary.get(key)
                if val is not None:
                    parts.append(self._fmt_kv(key, f"{val:.4g}", color))

        return "  ".join(parts)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _fmt_label(self, key: str, value: str, color: bool) -> str:
        label = f"{key}:{value}"
        if color:
            return f"{self._ANSI_BOLD}{self._ANSI_CYAN}{label}{self._ANSI_RESET}"
        return label

    def _fmt_kv(self, key: str, value: str, color: bool) -> str:
        if color:
            return f"{self._ANSI_BOLD}{key}{self._ANSI_RESET}:{value}"
        return f"{key}:{value}"
