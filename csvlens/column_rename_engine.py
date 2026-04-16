from __future__ import annotations


class ColumnRenameEngine:
    """Track user-defined renames for CSV columns."""

    def __init__(self, headers: list[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: list[str] = list(headers)
        self._renames: dict[str, str] = {}

    @property
    def headers(self) -> list[str]:
        return list(self._headers)

    @property
    def renames(self) -> dict[str, str]:
        return dict(self._renames)

    def set_rename(self, original: str, new_name: str) -> None:
        if original not in self._headers:
            raise KeyError(f"Column '{original}' not found")
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("new_name must not be blank")
        self._renames[original] = new_name

    def clear_rename(self, original: str) -> None:
        self._renames.pop(original, None)

    def clear_all(self) -> None:
        self._renames.clear()

    def display_headers(self) -> list[str]:
        """Return headers with renames applied."""
        return [self._renames.get(h, h) for h in self._headers]

    def original_for(self, display_name: str) -> str | None:
        """Return the original column name for a given display name."""
        for orig, disp in self._renames.items():
            if disp == display_name:
                return orig
        if display_name in self._headers:
            return display_name
        return None
