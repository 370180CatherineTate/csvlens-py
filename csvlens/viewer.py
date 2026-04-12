"""Viewer module: ties together CSVLoader, StatsReporter, and FilterEngine for CLI display."""

from typing import List, Optional, Dict
from csvlens.csv_loader import CSVLoader
from csvlens.stats_reporter import StatsReporter
from csvlens.filter_engine import FilterEngine


class Viewer:
    """Coordinates loading, filtering, and reporting for a CSV file."""

    def __init__(self, filepath: str):
        self._loader = CSVLoader(filepath)
        self._reporter = StatsReporter(self._loader)
        self._engine = FilterEngine(self._loader.headers)
        self._filtered_rows: Optional[List[List[str]]] = None

    @property
    def headers(self) -> List[str]:
        return self._loader.headers

    @property
    def total_rows(self) -> int:
        return self._loader.row_count

    def apply_filter(self, pattern: str, column: Optional[str] = None,
                     case_sensitive: bool = False) -> None:
        """Apply a global or column-scoped regex filter."""
        if column:
            self._engine.set_column_filter(column, pattern, case_sensitive)
        else:
            self._engine.set_global_filter(pattern, case_sensitive)
        self._filtered_rows = None  # invalidate cache

    def clear_filters(self) -> None:
        """Clear all active filters and reset the cached result."""
        self._engine.clear_filters()
        self._filtered_rows = None

    def get_rows(self, limit: Optional[int] = None) -> List[List[str]]:
        """Return filtered rows, optionally limited to `limit` rows."""
        if self._filtered_rows is None:
            all_rows = self._loader.rows
            self._filtered_rows = self._engine.apply(all_rows)
        if limit is not None:
            return self._filtered_rows[:limit]
        return self._filtered_rows

    @property
    def filtered_row_count(self) -> int:
        return len(self.get_rows())

    def get_column_stats(self, column: str) -> Dict:
        """Return statistics for a specific column."""
        return self._reporter.get(column)

    def summary(self) -> Dict:
        """Return a high-level summary of the current view state."""
        return {
            "file": self._loader.filepath,
            "total_rows": self.total_rows,
            "filtered_rows": self.filtered_row_count,
            "columns": len(self.headers),
            "active_filters": self._engine.active_filters,
        }
