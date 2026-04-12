"""CSV loading and parsing module for csvlens-py."""

import csv
from pathlib import Path
from typing import Iterator


class CSVLoader:
    """Loads and provides access to CSV file data."""

    def __init__(self, filepath: str, delimiter: str = ",", encoding: str = "utf-8"):
        self.filepath = Path(filepath)
        self.delimiter = delimiter
        self.encoding = encoding
        self._headers: list[str] = []
        self._row_count: int = 0

        if not self.filepath.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        if not self.filepath.is_file():
            raise ValueError(f"Path is not a file: {filepath}")

        self._scan_metadata()

    def _scan_metadata(self) -> None:
        """Read headers and count rows without loading all data into memory."""
        with self.filepath.open(encoding=self.encoding, newline="") as fh:
            reader = csv.reader(fh, delimiter=self.delimiter)
            try:
                self._headers = next(reader)
            except StopIteration:
                raise ValueError("CSV file is empty or has no header row.")
            self._row_count = sum(1 for _ in reader)

    @property
    def headers(self) -> list[str]:
        """Return the list of column headers."""
        return list(self._headers)

    @property
    def row_count(self) -> int:
        """Return the total number of data rows (excluding header)."""
        return self._row_count

    @property
    def column_count(self) -> int:
        """Return the number of columns."""
        return len(self._headers)

    def iter_rows(self) -> Iterator[dict[str, str]]:
        """Yield each data row as an ordered dict keyed by header name."""
        with self.filepath.open(encoding=self.encoding, newline="") as fh:
            reader = csv.DictReader(fh, delimiter=self.delimiter)
            for row in reader:
                yield dict(row)

    def load_rows(self, limit: int | None = None) -> list[dict[str, str]]:
        """Load rows into memory, optionally capped at *limit* rows."""
        rows: list[dict[str, str]] = []
        for i, row in enumerate(self.iter_rows()):
            if limit is not None and i >= limit:
                break
            rows.append(row)
        return rows

    def __repr__(self) -> str:
        return (
            f"CSVLoader(filepath={self.filepath!r}, "
            f"columns={self.column_count}, rows={self.row_count})"
        )
