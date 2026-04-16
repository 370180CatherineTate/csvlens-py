from __future__ import annotations

from csvlens.column_rating_engine import ColumnRatingEngine


class RatingStatusBar:
    """One-line status bar summarising column ratings."""

    def __init__(self, engine: ColumnRatingEngine, width: int = 80) -> None:
        if width < 10:
            raise ValueError("width must be at least 10")
        self._engine = engine
        self._width = width

    @property
    def width(self) -> int:
        return self._width

    def render(self) -> str:
        ratings = self._engine.ratings
        if not ratings:
            msg = "No column ratings set"
        else:
            parts = [
                f"{col}={'★'*r}" for col, r in sorted(ratings.items(), key=lambda x: -x[1])
            ]
            msg = "Ratings: " + "  ".join(parts)
        if len(msg) > self._width:
            msg = msg[: self._width - 1] + "…"
        return msg.ljust(self._width)

    def __str__(self) -> str:
        return self.render()
