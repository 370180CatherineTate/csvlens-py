"""Tests for ColumnHeatmapRenderer."""
import pytest
from csvlens.column_heatmap_engine import ColumnHeatmapEngine
from csvlens.column_heatmap_renderer import ColumnHeatmapRenderer


ROWS = [
    {"score": "10", "label": "alpha"},
    {"score": "50", "label": "beta"},
    {"score": "90", "label": "gamma"},
]


@pytest.fixture
def engine():
    e = ColumnHeatmapEngine(["score", "label"], ROWS)
    e.enable("score")
    return e


@pytest.fixture
def renderer(engine):
    return ColumnHeatmapRenderer(engine, col_width=10)


def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError, match="col_width"):
        ColumnHeatmapRenderer(engine, col_width=0)


def test_col_width_property(renderer):
    assert renderer.col_width == 10


def test_render_header_returns_string(renderer):
    result = renderer.render_header()
    assert isinstance(result, str)


def test_render_header_contains_columns(renderer):
    result = renderer.render_header()
    assert "score" in result
    assert "label" in result


def test_render_row_returns_string(renderer):
    result = renderer.render_row(ROWS[0])
    assert isinstance(result, str)


def test_render_row_contains_values(renderer):
    result = renderer.render_row(ROWS[0])
    assert "10" in result
    assert "alpha" in result


def test_render_row_hot_cell_has_ansi(renderer):
    # The max value should receive an ANSI background escape
    result = renderer.render_row(ROWS[2])  # score=90 is max
    assert "\x1b[" in result


def test_render_row_no_heat_no_ansi_for_label(renderer):
    # label column is not enabled, so no ANSI escape expected for its cell
    result = renderer.render_row(ROWS[0])
    # Split on separator and check the label part has no background code
    parts = result.split(" | ")
    label_part = parts[1]
    assert "\x1b[48;5;" not in label_part


def test_render_row_truncates_long_value():
    rows = [{"val": "A" * 20}]
    eng = ColumnHeatmapEngine(["val"], rows)
    rend = ColumnHeatmapRenderer(eng, col_width=8)
    result = rend.render_row(rows[0])
    # Cell should be padded/truncated to col_width
    cell = result.strip()
    assert len(cell) <= 8 + 1  # allow for ellipsis char
