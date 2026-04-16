from __future__ import annotations
from typing import Dict, List, Optional


class ColumnPivotEngine:
    """Pivot rows by a key column, aggregating a value column."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers = list(headers)
        self._key_column: Optional[str] = None
        self._value_column: Optional[str] = None
        self._agg: str = "count"

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def key_column(self) -> Optional[str]:
        return self._key_column

    @property
    def value_column(self) -> Optional[str]:
        return self._value_column

    @property
    def agg(self) -> str:
        return self._agg

    def configure(self, key_column: str, value_column: str, agg: str = "count") -> None:
        if key_column not in self._headers:
            raise ValueError(f"key_column '{key_column}' not in headers")
        if value_column not in self._headers:
            raise ValueError(f"value_column '{value_column}' not in headers")
        if agg not in ("count", "sum", "mean"):
            raise ValueError(f"agg must be 'count', 'sum', or 'mean'; got '{agg}'")
        self._key_column = key_column
        self._value_column = value_column
        self._agg = agg

    def pivot(self, rows: List[Dict[str, str]]) -> Dict[str, float]:
        if self._key_column is None or self._value_column is None:
            raise RuntimeError("configure() must be called before pivot()")
        buckets: Dict[str, List[float]] = {}
        for row in rows:
            key = row.get(self._key_column, "")
            raw = row.get(self._value_column, "")
            try:
                val = float(raw)
            except (ValueError, TypeError):
                val = 0.0
            buckets.setdefault(key, []).append(val)
        result: Dict[str, float] = {}
        for key, vals in buckets.items():
            if self._agg == "count":
                result[key] = float(len(vals))
            elif self._agg == "sum":
                result[key] = sum(vals)
            else:
                result[key] = sum(vals) / len(vals) if vals else 0.0
        return result

    def reset(self) -> None:
        self._key_column = None
        self._value_column = None
        self._agg = "count"
