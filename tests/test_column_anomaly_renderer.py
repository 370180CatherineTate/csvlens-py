"""Tests for ColumnAnomalyRenderer."""
import pytest
from csvlens.column_anomaly_engine import ColumnAnomalyEngine
from csvlens.column_anomaly_renderer import ColumnAnomalyRenderer


HEADERS = ["score", "name"]
ROWS = [
    {"score": str(v), "name": "item"}
    for v in [5, 6, 5, 7, 6, 5, 6, 200, 5, 6]
]


@pytest.fixture
def engine():
    return ColumnAnomalyEngine(HEADERS, ROWS)


@pytest.fixture
def renderer(engine):
    return ColumnAnomalyRenderer(engine, col_width=14)


def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError, match="col_width must be at least 6"):
        ColumnAnomalyRenderer(engine, col_width=3)


def test_col_width_property(renderer):
    assert renderer.col_width == 14


def test_render_header_returns_string(renderer):
    result = renderer.render_header()
    assert isinstance(result, str)


def test_render_header_contains_columns(renderer):
    result = renderer.render_header()
    assert "score" in result
    assert "name" in result


def test_render_row_returns_string(renderer):
    row = {"score": "200", "name": "item"}
    result = renderer.render_row(row)
    assert isinstance(result, str)


def test_render_row_highlights_outlier(renderer):
    row = {"score": "200", "name": "item"}
    result = renderer.render_row(row)
    assert "\033[31m" in result


def test_render_row_no_highlight_normal(renderer):
    row = {"score": "5", "name": "item"}
    result = renderer.render_row(row)
    assert "\033[31m" not in result


def test_render_summary_returns_string(renderer):
    result = renderer.render_summary()
    assert isinstance(result, str)
    assert "score" in result
    assert "name" in result


def test_render_row_fits_col_width(renderer):
    row = {"score": "A" * 100, "name": "B" * 100}
    result = renderer.render_row(row)
    for segment in result.split(" | "):
        visible = segment.replace("\033[31m", "").replace("\033[32m", "").replace("\033[0m", "")
        assert len(visible) <= renderer.col_width + 1
