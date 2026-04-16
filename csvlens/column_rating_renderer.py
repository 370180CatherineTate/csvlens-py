from __future__ import annotations

from typing import List

from csvlens.column_rating_engine import ColumnRatingEngine

_STARS = "★"
_EMPTY = "☆"


class ColumnRatingRenderer:
    """Render column ratings as star strings inside a fixed-width cell."""

    def __init__(self, engine: ColumnRatingEngine, col_width: int = 20) -> None:
        if col_width < 5:
            raise ValueError("col_width must be at least 5")
        self._engine = engine
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _fit(self, text: str) -> str:
        if len(text) > self._col_width:
            return text[: self._col_width - 1] + "…"
        return text.ljust(self._col_width)

    def _stars(self, column: str) -> str:
        rating = self._engine.get_rating(column)
        if rating is None:
            return _EMPTY * ColumnRatingEngine.MAX_RATING
        filled = _STARS * rating
        empty = _EMPTY * (ColumnRatingEngine.MAX_RATING - rating)
        return filled + empty

    def render_header(self) -> str:
        parts = [self._fit(h) for h in self._engine.headers]
        return " | ".join(parts)

    def render_ratings(self) -> str:
        parts = [self._fit(self._stars(h)) for h in self._engine.headers]
        return " | ".join(parts)

    def render(self) -> str:
        return self.render_header() + "\n" + render_ratings_line(self)


def render_ratings_line(r: ColumnRatingRenderer) -> str:
    return r.render_ratings()
