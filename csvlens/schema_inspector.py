"""Inspects and infers column data types from CSV rows."""

from __future__ import annotations

import re
from typing import Dict, List, Optional

_INT_RE = re.compile(r'^-?\d+$')
_FLOAT_RE = re.compile(r'^-?\d+\.\d*$|^-?\.\d+$')
_BOOL_VALUES = {"true", "false", "yes", "no", "1", "0"}
_DATE_RE = re.compile(
    r'^\d{4}-\d{2}-\d{2}$'
    r'|^\d{2}/\d{2}/\d{4}$'
    r'|^\d{2}-\d{2}-\d{4}$'
)


def _infer_cell_type(value: str) -> str:
    v = value.strip()
    if v == "":
        return "null"
    if _INT_RE.match(v):
        return "integer"
    if _FLOAT_RE.match(v):
        return "float"
    if v.lower() in _BOOL_VALUES:
        return "boolean"
    if _DATE_RE.match(v):
        return "date"
    return "string"


class SchemaInspector:
    """Infers column types by sampling rows."""

    SUPPORTED_TYPES = ("integer", "float", "boolean", "date", "string", "null")

    def __init__(self, headers: List[str], sample_rows: List[Dict[str, str]]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers = list(headers)
        self._sample_rows = list(sample_rows)
        self._schema: Dict[str, str] = {}
        self._inspect()

    def _inspect(self) -> None:
        type_votes: Dict[str, Dict[str, int]] = {h: {} for h in self._headers}
        for row in self._sample_rows:
            for header in self._headers:
                cell_type = _infer_cell_type(row.get(header, ""))
                type_votes[header][cell_type] = type_votes[header].get(cell_type, 0) + 1

        priority = ["float", "integer", "boolean", "date", "string", "null"]
        for header in self._headers:
            votes = type_votes[header]
            non_null = {t: c for t, c in votes.items() if t != "null"}
            if not non_null:
                self._schema[header] = "null"
                continue
            for t in priority:
                if t in non_null:
                    self._schema[header] = t
                    break
            else:
                self._schema[header] = "string"

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def schema(self) -> Dict[str, str]:
        """Return a mapping of column name -> inferred type."""
        return dict(self._schema)

    def type_of(self, column: str) -> Optional[str]:
        """Return the inferred type for a specific column, or None."""
        return self._schema.get(column)

    def columns_of_type(self, type_name: str) -> List[str]:
        """Return all column names inferred as *type_name*."""
        return [h for h in self._headers if self._schema.get(h) == type_name]
