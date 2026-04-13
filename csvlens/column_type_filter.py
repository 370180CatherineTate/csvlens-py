"""Filter rows based on inferred column data types."""

from typing import List, Dict, Optional

_VALID_TYPES = {"integer", "float", "boolean", "date", "string"}


def _infer_type(value: str) -> str:
    """Infer the type of a single cell value."""
    v = value.strip()
    if v == "":
        return "string"
    try:
        int(v)
        return "integer"
    except ValueError:
        pass
    try:
        float(v)
        return "float"
    except ValueError:
        pass
    if v.lower() in ("true", "false", "yes", "no"):
        return "boolean"
    # Simple ISO date check: YYYY-MM-DD
    parts = v.split("-")
    if len(parts) == 3 and all(p.isdigit() for p in parts) and len(parts[0]) == 4:
        return "date"
    return "string"


class ColumnTypeFilter:
    """Filter rows by requiring a specific inferred type for a given column."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers = list(headers)
        self._rules: Dict[str, str] = {}

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def rules(self) -> Dict[str, str]:
        """Return a copy of the active column-type rules."""
        return dict(self._rules)

    def set_rule(self, column: str, type_name: str) -> None:
        """Require *column* to match *type_name* for a row to pass."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        type_name = type_name.lower()
        if type_name not in _VALID_TYPES:
            raise ValueError(
                f"Invalid type {type_name!r}. Valid types: {sorted(_VALID_TYPES)}"
            )
        self._rules[column] = type_name

    def clear_rule(self, column: Optional[str] = None) -> None:
        """Remove the rule for *column*, or all rules if *column* is None."""
        if column is None:
            self._rules.clear()
        else:
            self._rules.pop(column, None)

    def apply(self, rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Return only rows that satisfy all active type rules."""
        if not self._rules:
            return list(rows)
        result = []
        for row in rows:
            if all(
                _infer_type(row.get(col, "")) == expected
                for col, expected in self._rules.items()
            ):
                result.append(row)
        return result
