"""Pagination module for navigating large CSV datasets in chunks."""

from typing import List, Optional


class Paginator:
    """Handles page-based navigation over a list of rows."""

    def __init__(self, rows: List[dict], page_size: int = 20):
        """
        Initialize the Paginator.

        Args:
            rows: Full list of row dicts to paginate over.
            page_size: Number of rows per page. Defaults to 20.
        """
        if page_size < 1:
            raise ValueError("page_size must be at least 1")
        self._rows = rows
        self._page_size = page_size
        self._current_page = 0

    @property
    def page_size(self) -> int:
        return self._page_size

    @property
    def total_rows(self) -> int:
        return len(self._rows)

    @property
    def total_pages(self) -> int:
        if self.total_rows == 0:
            return 0
        return (self.total_rows + self._page_size - 1) // self._page_size

    @property
    def current_page(self) -> int:
        return self._current_page

    def get_page(self, page: Optional[int] = None) -> List[dict]:
        """Return rows for the given page index (0-based). Uses current page if None."""
        if page is not None:
            if page < 0 or (self.total_pages > 0 and page >= self.total_pages):
                raise IndexError(f"Page {page} is out of range (0-{self.total_pages - 1})")
            self._current_page = page
        start = self._current_page * self._page_size
        end = start + self._page_size
        return self._rows[start:end]

    def next_page(self) -> List[dict]:
        """Advance to the next page and return its rows."""
        if self._current_page + 1 >= self.total_pages:
            raise IndexError("Already on the last page")
        self._current_page += 1
        return self.get_page()

    def prev_page(self) -> List[dict]:
        """Go back to the previous page and return its rows."""
        if self._current_page <= 0:
            raise IndexError("Already on the first page")
        self._current_page -= 1
        return self.get_page()

    def reset(self) -> None:
        """Reset to the first page."""
        self._current_page = 0

    def is_first_page(self) -> bool:
        return self._current_page == 0

    def is_last_page(self) -> bool:
        return self.total_pages == 0 or self._current_page == self.total_pages - 1
