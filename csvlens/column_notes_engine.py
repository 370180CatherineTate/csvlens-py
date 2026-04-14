"""Engine for attaching user notes/annotations to columns."""
from __future__ import annotations


class ColumnNotesEngine:
    """Attach and retrieve plain-text notes for individual columns."""

    def __init__(self, headers: list[str]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        self._headers: list[str] = list(headers)
        self._notes: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def headers(self) -> list[str]:
        """Return the original column headers."""
        return list(self._headers)

    @property
    def notes(self) -> dict[str, str]:
        """Return a copy of all current notes keyed by column name."""
        return dict(self._notes)

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def set_note(self, column: str, text: str) -> None:
        """Set (or overwrite) the note for *column*.

        Parameters
        ----------
        column:
            Must be one of the known headers.
        text:
            Arbitrary annotation string; leading/trailing whitespace is
            stripped before storage.  An empty string after stripping
            removes the note entirely.
        """
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        stripped = text.strip()
        if stripped:
            self._notes[column] = stripped
        else:
            self._notes.pop(column, None)

    def get_note(self, column: str) -> str | None:
        """Return the note for *column*, or ``None`` if none is set."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        return self._notes.get(column)

    def clear_note(self, column: str) -> None:
        """Remove the note for *column* (no-op if not set)."""
        if column not in self._headers:
            raise KeyError(f"Unknown column: {column!r}")
        self._notes.pop(column, None)

    def clear_all(self) -> None:
        """Remove all notes."""
        self._notes.clear()

    def annotated_columns(self) -> list[str]:
        """Return headers that currently have a note, in original order."""
        return [h for h in self._headers if h in self._notes]
