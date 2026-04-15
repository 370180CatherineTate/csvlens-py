"""Engine for defining computed columns via simple Python expressions."""
from __future__ import annotations

from typing import Dict, List, Optional


class ColumnFormulaEngine:
    """Manages named formula columns derived from existing CSV columns."""

    def __init__(self, headers: List[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: List[str] = list(headers)
        self._formulas: Dict[str, str] = {}

    @property
    def headers(self) -> List[str]:
        """Original (base) headers — does not include formula columns."""
        return list(self._headers)

    @property
    def formula_names(self) -> List[str]:
        """Names of all currently registered formula columns."""
        return list(self._formulas.keys())

    @property
    def formulas(self) -> Dict[str, str]:
        """Mapping of formula-column name -> expression string."""
        return dict(self._formulas)

    def set_formula(self, name: str, expression: str) -> None:
        """Register or update a formula column."""
        if not name or not name.strip():
            raise ValueError("Formula name must not be empty")
        if not expression or not expression.strip():
            raise ValueError("Expression must not be empty")
        self._formulas[name] = expression

    def remove_formula(self, name: str) -> None:
        """Remove a formula column by name."""
        if name not in self._formulas:
            raise KeyError(f"No formula named '{name}'")
        del self._formulas[name]

    def clear(self) -> None:
        """Remove all formula columns."""
        self._formulas.clear()

    def evaluate_row(self, name: str, row: Dict[str, str]) -> Optional[str]:
        """Evaluate a named formula against a single row dict.

        The expression may reference any base column by its header name.
        Returns the string result, or None on evaluation error.
        """
        if name not in self._formulas:
            raise KeyError(f"No formula named '{name}'")
        expr = self._formulas[name]
        safe_globals = {"__builtins__": {}}
        # Expose numeric-coerced values where possible
        local_vars: Dict[str, object] = {}
        for k, v in row.items():
            try:
                local_vars[k] = float(v) if '.' in v else int(v)
            except (ValueError, TypeError):
                local_vars[k] = v
        try:
            result = eval(expr, safe_globals, local_vars)  # noqa: S307
            return str(result)
        except Exception:
            return None

    def apply(self, rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Return a new list of rows with all formula columns appended."""
        output = []
        for row in rows:
            new_row = dict(row)
            for name in self._formulas:
                new_row[name] = self.evaluate_row(name, row) or ""
            output.append(new_row)
        return output
