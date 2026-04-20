"""High-level viewer that wires together loading, filtering, sorting,
and pagination for the interactive TUI."""

from typing import List, Dict, Optional

from csvlens.csv_loader import CSVLoader
from csvlens.filter_engine import FilterEngine
from csvlens.sort_engine import SortEngine
from csvlens.pagination import Paginator


class Viewer:
    """Facade that coordinates all data-access components."""

    def __init__(self, path: str, page_size: int = 25) -> None:
        self._loader = CSVLoader(path)
        self._filter = FilterEngine(self._loader.headers)
        self._sorter = SortEngine(self._loader.headers)
        self._page_size = page_size
        self._paginator: Optional[Paginator] = None
        self._rebuild()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def headers(self) -> List[str]:
        return self._loader.headers

    @property
    def total_rows(self) -> int:
        return self._paginator.total_rows  # type: ignore[union-attr]

    @property
    def total_pages(self) -> int:
        """Total number of pages given the current filter/sort state."""
        assert self._paginator is not None
        return self._paginator.total_pages

    # ------------------------------------------------------------------
    # Filter helpers
    # ------------------------------------------------------------------

    def apply_filter(self, pattern: str) -> None:
        """Apply a global regex filter and rebuild the paginator."""
        self._filter.set_global_filter(pattern)
        self._rebuild()

    def apply_column_filter(self, column: str, pattern: str) -> None:
        self._filter.set_column_filter(column, pattern)
        self._rebuild()

    def clear_filters(self) -> None:
        self._filter.clear_filters()
        self._rebuild()

    # ------------------------------------------------------------------
    # Sort helpers
    # ------------------------------------------------------------------

    def apply_sort(self, column: str, ascending: bool = True) -> None:
        """Sort visible rows by *column* and rebuild the paginator."""
        self._sorter.set_sort(column, ascending)
        self._rebuild()

    def clear_sort(self) -> None:
        self._sorter.clear_sort()
        self._rebuild()

    # ------------------------------------------------------------------
    # Page access
    # ------------------------------------------------------------------

    def get_page(self, page: int) -> List[Dict[str, str]]:
        """Return rows for the requested 1-based page number."""
        assert self._paginator is not None
        return self._paginator.get_page(page)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _rebuild(self) -> None:
        """Re-apply filter + sort and recreate the paginator."""
        rows = self._loader.rows
        rows = self._filter.apply(rows)
        rows = self._sorter.sort(rows)
        self._paginator = Paginator(rows, page_size=self._page_size)
