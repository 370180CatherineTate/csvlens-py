from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple


class ValidationRule:
    """A single validation rule applied to a column."""

    def __init__(self, rule_type: str, param: Optional[str] = None) -> None:
        valid_types = {"not_empty", "numeric", "regex", "max_len"}
        if rule_type not in valid_types:
            raise ValueError(f"rule_type must be one of {sorted(valid_types)}")
        if rule_type == "regex" and not param:
            raise ValueError("regex rule requires a non-empty pattern param")
        if rule_type == "max_len":
            if param is None or not str(param).isdigit() or int(param) < 1:
                raise ValueError("max_len rule requires a positive integer param")
        self.rule_type = rule_type
        self.param = param

    def check(self, value: str) -> bool:
        """Return True if value passes the rule."""
        if self.rule_type == "not_empty":
            return value.strip() != ""
        if self.rule_type == "numeric":
            try:
                float(value)
                return True
            except ValueError:
                return False
        if self.rule_type == "regex":
            return bool(re.search(self.param, value))
        if self.rule_type == "max_len":
            return len(value) <= int(self.param)
        return True  # pragma: no cover


class ColumnValidationEngine:
    """Validates rows against per-column rules."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._rules: Dict[str, List[ValidationRule]] = {}

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def rules(self) -> Dict[str, List[ValidationRule]]:
        return {k: list(v) for k, v in self._rules.items()}

    def add_rule(self, column: str, rule: ValidationRule) -> None:
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        self._rules.setdefault(column, []).append(rule)

    def clear_rules(self, column: str) -> None:
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        self._rules.pop(column, None)

    def validate_row(self, row: Dict[str, str]) -> Dict[str, List[str]]:
        """Return a mapping of column -> list of failed rule descriptions."""
        errors: Dict[str, List[str]] = {}
        for col, rule_list in self._rules.items():
            cell = row.get(col, "")
            for rule in rule_list:
                if not rule.check(cell):
                    errors.setdefault(col, []).append(
                        rule.rule_type
                        if rule.param is None
                        else f"{rule.rule_type}:{rule.param}"
                    )
        return errors

    def validate_rows(
        self, rows: List[Dict[str, str]]
    ) -> List[Tuple[int, Dict[str, List[str]]]]:
        """Return list of (row_index, errors) for rows with at least one error."""
        results = []
        for idx, row in enumerate(rows):
            errs = self.validate_row(row)
            if errs:
                results.append((idx, errs))
        return results
