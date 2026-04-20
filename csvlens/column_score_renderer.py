from __future__ import annotations

from typing import Dict, List, Optional

from csvlens.column_score_engine import ColumnScoreEngine


class ColumnScoreRenderer:
    """Render a score column appended to each data row."""

    def __init__(self, engine: ColumnScoreEngine, col_width: int = 10) -> None:
        if col_width < 4:
            raise ValueError("col_width must be >= 4")
        self._engine = engine
        self._col_width = col_width

    @property
    def col_width(self) -> int:
        return self._col_width

    def _fit(self, text: str) -> str:
        if len(text) > self._col_width:
            return text[: self._col_width - 1] + "…"
        return text.ljust(self._col_width)

    def render_header(self) -> str:
        return self._fit("[score]")

    def render_score(self, score: Optional[float]) -> str:
        if score is None:
            return self._fit("n/a")
        return self._fit(f"{score:.4g}")

    def render_row(self, row: Dict[str, str]) -> str:
        score = self._engine.score_row(row)
        return self.render_score(score)

    def render_all(
        self, rows: List[Dict[str, str]], include_header: bool = True
    ) -> List[str]:
        lines: List[str] = []
        if include_header:
            lines.append(self.render_header())
        for row in rows:
            lines.append(self.render_row(row))
        return lines
