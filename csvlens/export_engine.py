"""Export filtered/sorted rows to CSV or JSON output."""

import csv
import json
import io
from typing import List, Dict, Optional


class ExportEngine:
    """Handles exporting visible rows to CSV or JSON format."""

    SUPPORTED_FORMATS = ("csv", "json")

    def __init__(self, headers: List[str]):
        if not headers:
            raise ValueError("Headers must not be empty.")
        self._headers = list(headers)

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    def to_csv(self, rows: List[Dict[str, str]], visible_columns: Optional[List[str]] = None) -> str:
        """Serialize rows to CSV string, optionally restricting to visible columns."""
        columns = self._resolve_columns(visible_columns)
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=columns,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()

    def to_json(self, rows: List[Dict[str, str]], visible_columns: Optional[List[str]] = None) -> str:
        """Serialize rows to JSON string, optionally restricting to visible columns."""
        columns = self._resolve_columns(visible_columns)
        filtered = [
            {col: row.get(col, "") for col in columns}
            for row in rows
        ]
        return json.dumps(filtered, indent=2, ensure_ascii=False)

    def export(self, rows: List[Dict[str, str]], fmt: str, visible_columns: Optional[List[str]] = None) -> str:
        """Dispatch export to the appropriate format handler."""
        fmt = fmt.lower()
        if fmt not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format '{fmt}'. Choose from {self.SUPPORTED_FORMATS}.")
        if fmt == "csv":
            return self.to_csv(rows, visible_columns)
        return self.to_json(rows, visible_columns)

    def _resolve_columns(self, visible_columns: Optional[List[str]]) -> List[str]:
        if visible_columns is None:
            return self._headers
        unknown = set(visible_columns) - set(self._headers)
        if unknown:
            raise ValueError(f"Unknown columns: {unknown}")
        return [c for c in self._headers if c in visible_columns]
