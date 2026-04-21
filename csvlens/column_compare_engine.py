"""Engine for comparing two columns cell-by-cell with configurable modes."""
from __future__ import annotations

from typing import List, Dict, Optional, Tuple


_MODES = {"eq", "ne", "lt", "le", "gt", "ge", "diff"}


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


class CompareResult:
    def __init__(self, left: str, right: str, mode: str) -> None:
        self._left = left
        self._right = right
        self._mode = mode
        self._match: Optional[bool] = None
        self._diff: Optional[float] = None
        self._compute()

    def _compute(self) -> None:
        lf = _to_float(self._left)
        rf = _to_float(self._right)
        if self._mode == "diff":
            if lf is not None and rf is not None:
                self._diff = lf - rf
            return
        ops = {
            "eq": lambda a, b: a == b,
            "ne": lambda a, b: a != b,
            "lt": lambda a, b: a < b,
            "le": lambda a, b: a <= b,
            "gt": lambda a, b: a > b,
            "ge": lambda a, b: a >= b,
        }
        if lf is not None and rf is not None:
            self._match = ops[self._mode](lf, rf)
        else:
            self._match = ops[self._mode](self._left, self._right)

    @property
    def match(self) -> Optional[bool]:
        return self._match

    @property
    def diff(self) -> Optional[float]:
        return self._diff

    def label(self) -> str:
        if self._mode == "diff":
            return f"{self._diff:+.4g}" if self._diff is not None else "N/A"
        return "✓" if self._match else "✗"


class ColumnCompareEngine:
    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers = list(headers)
        self._rules: Dict[Tuple[str, str], str] = {}

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def rules(self) -> Dict[Tuple[str, str], str]:
        return dict(self._rules)

    def set_rule(self, col_a: str, col_b: str, mode: str = "diff") -> None:
        if col_a not in self._headers:
            raise KeyError(f"column not found: {col_a!r}")
        if col_b not in self._headers:
            raise KeyError(f"column not found: {col_b!r}")
        if mode not in _MODES:
            raise ValueError(f"mode must be one of {sorted(_MODES)}, got {mode!r}")
        self._rules[(col_a, col_b)] = mode

    def clear_rule(self, col_a: str, col_b: str) -> None:
        self._rules.pop((col_a, col_b), None)

    def compare_row(self, row: Dict[str, str]) -> Dict[Tuple[str, str], CompareResult]:
        out: Dict[Tuple[str, str], CompareResult] = {}
        for (col_a, col_b), mode in self._rules.items():
            left = row.get(col_a, "")
            right = row.get(col_b, "")
            out[(col_a, col_b)] = CompareResult(left, right, mode)
        return out
