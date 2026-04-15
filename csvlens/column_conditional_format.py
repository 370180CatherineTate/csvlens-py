"""Conditional formatting engine: apply colour rules to cells based on value thresholds."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

# ANSI colour helpers
_RESET = "\033[0m"
_COLOURS: Dict[str, str] = {
    "red":     "\033[31m",
    "green":   "\033[32m",
    "yellow":  "\033[33m",
    "blue":    "\033[34m",
    "magenta": "\033"cyan":    "\033[OPS ="<",<=", ">", 


class Con:
    """A threshold rule: (operator, threshold, colour)."""

    def __init__(self, operator: str, threshold: float, colour: str) -> None:
        if operator not in _OPS:
            raise ValueError(f"operator must be one of {sorted(_OPS)}, got {operator!r}")
        if colour not in _COLOURS:
            raise ValueError(f"colour must be one of {sorted(_COLOURS)}, got {colour!r}")
        self._op = operator
        self._threshold = threshold
        self._colour = colour

    @property
    def operator(self) -> str:
        return self._op

    @property
    def threshold(self) -> float:
        return self._threshold

    @property
    def colour(self) -> str:
        return self._colour

    def matches(self, value: float) -> bool:
        ops = {
            "<":  value <  self._threshold,
            "<=": value <= self._threshold,
            ">": value >  self._threshold,
            ">=": value >= self._threshold,
            "==": value == self._threshold,
            "!=": value != self._threshold,
        }
        return ops[self._op]


class ColumnConditionalFormat:
    """Manages per-column conditional formatting rules."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._rules: Dict[str, List[ConditionalRule]] = {h: [] for h in headers}

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    def add_rule(self, column: str, operator: str, threshold: float, colour: str) -> None:
        """Append a conditional rule to *column*."""
        if column not in self._rules:
            raise KeyError(f"unknown column: {column!r}")
        self._rules[column].append(ConditionalRule(operator, threshold, colour))

    def clear_rules(self, column: str) -> None:
        if column not in self._rules:
            raise KeyError(f"unknown column: {column!r}")
        self._rules[column] = []

    def rules_for(self, column: str) -> List[ConditionalRule]:
        if column not in self._rules:
            raise KeyError(f"unknown column: {column!r}")
        return list(self._rules[column])

    def format_cell(self, column: str, raw: str) -> str:
        """Return *raw* wrapped in ANSI colour if any rule matches; otherwise unchanged."""
        if column not in self._rules:
            return raw
        try:
            value = float(raw)
        except (ValueError, TypeError):
            return raw
        for rule in self._rules[column]:
            if rule.matches(value):
                return f"{_COLOURS[rule.colour]}{raw}{_RESET}"
        return raw
