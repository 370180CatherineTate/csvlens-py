"""Tests for ColumnColorRenderer."""
import pytest
from csvlens.column_color_engine import ColumnColorEngine
from csvlens.column_color_renderer import ColumnColorRenderer


@pytest.fixture
def engine():
    e = ColumnColorEngine(["name", "age", "city"])
    e.set_color("name", "cyan")
    e.set_color("age", "yellow")
    return e


@pytest.fixture
def renderer(engine):
    return ColumnColorRenderer(engine, col_width=12)


def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError, match="col_width"):
        ColumnColorRenderer(engine, col_width=2)


def test_col_width_property(renderer):
    assert renderer.col_width == 12


def test_render_header_returns_string(renderer):
    result = renderer.render_header()
    assert isinstance(result, str)


def test_render_header_contains_columns(renderer):
    result = renderer.render_header()
    assert "name" in result
    assert "age" in result
    assert "city" in result


def test_render_header_has_ansi_codes(renderer):
    result = renderer.render_header()
    assert "\033[" in result  # at least one colored column


def test_render_row_returns_string(renderer):
    row = {"name": "Alice", "age": "30", "city": "Paris"}
    result = renderer.render_row(row)
    assert isinstance(result, str)


def test_render_row_contains_values(renderer):
    row = {"name": "Alice", "age": "30", "city": "Paris"}
    result = renderer.render_row(row)
    assert "Alice" in result
    assert "30" in result
    assert "Paris" in result


def test_render_row_missing_key_uses_empty(renderer):
    row = {"name": "Bob"}  # age and city missing
    result = renderer.render_row(row)
    assert "Bob" in result


def test_render_row_truncates_long_value(renderer):
    row = {"name": "A" * 50, "age": "25", "city": "X"}
    result = renderer.render_row(row)
    assert "…" in result


def test_render_all_includes_header_and_rows(renderer):
    rows = [
        {"name": "Alice", "age": "30", "city": "Paris"},
        {"name": "Bob", "age": "25", "city": "Rome"},
    ]
    result = renderer.render_all(rows)
    lines = result.split("\n")
    assert len(lines) == 3  # header + 2 rows
    assert "Alice" in result
    assert "Bob" in result


def test_render_all_empty_rows(renderer):
    result = renderer.render_all([])
    lines = result.split("\n")
    assert len(lines) == 1  # only header
