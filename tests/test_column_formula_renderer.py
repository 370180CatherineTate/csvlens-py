"""Tests for ColumnFormulaRenderer."""
import pytest
from csvlens.column_formula_engine import ColumnFormulaEngine
from csvlens.column_formula_renderer import ColumnFormulaRenderer


@pytest.fixture
def engine():
    e = ColumnFormulaEngine(["name", "price", "qty"])
    e.set_formula("total", "price * qty")
    return e


@pytest.fixture
def renderer(engine):
    return ColumnFormulaRenderer(engine, col_width=10)


def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError):
        ColumnFormulaRenderer(engine, col_width=2)


def test_col_width_property(renderer):
    assert renderer.col_width == 10


def test_render_header_returns_string(renderer):
    assert isinstance(renderer.render_header(), str)


def test_render_header_contains_base_columns(renderer):
    header = renderer.render_header()
    assert "name" in header
    assert "price" in header
    assert "qty" in header


def test_render_header_contains_formula_column(renderer):
    header = renderer.render_header()
    assert "total" in header


def test_render_row_returns_string(renderer):
    row = {"name": "apple", "price": "3", "qty": "4"}
    assert isinstance(renderer.render_row(row), str)


def test_render_row_contains_computed_value(renderer):
    row = {"name": "apple", "price": "3", "qty": "4"}
    result = renderer.render_row(row)
    assert "12" in result


def test_render_row_contains_base_values(renderer):
    row = {"name": "apple", "price": "3", "qty": "4"}
    result = renderer.render_row(row)
    assert "apple" in result


def test_render_all_returns_string(renderer):
    rows = [{"name": "a", "price": "2", "qty": "5"}]
    assert isinstance(renderer.render_all(rows), str)


def test_render_all_has_multiple_lines(renderer):
    rows = [
        {"name": "a", "price": "2", "qty": "5"},
        {"name": "b", "price": "3", "qty": "2"},
    ]
    lines = renderer.render_all(rows).splitlines()
    assert len(lines) == 3  # header + 2 data rows


def test_render_no_formulas_still_works():
    e = ColumnFormulaEngine(["x", "y"])
    r = ColumnFormulaRenderer(e, col_width=8)
    row = {"x": "1", "y": "2"}
    result = r.render_row(row)
    assert "1" in result and "2" in result


def test_long_value_is_truncated(renderer):
    row = {"name": "a" * 50, "price": "1", "qty": "1"}
    result = renderer.render_row(row)
    assert "\u2026" in result
