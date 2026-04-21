"""Tests for ColumnCompareRenderer."""
import pytest
from csvlens.column_compare_engine import ColumnCompareEngine
from csvlens.column_compare_renderer import ColumnCompareRenderer


@pytest.fixture
def engine():
    e = ColumnCompareEngine(["price", "cost", "qty"])
    e.set_rule("price", "cost", "diff")
    return e


@pytest.fixture
def renderer(engine):
    return ColumnCompareRenderer(engine, col_width=14)


def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError, match="col_width must be at least 4"):
        ColumnCompareRenderer(engine, col_width=3)


def test_col_width_property(renderer):
    assert renderer.col_width == 14


def test_render_header_returns_string(renderer):
    header = renderer.render_header()
    assert isinstance(header, str)


def test_render_header_contains_columns(renderer):
    header = renderer.render_header()
    assert "price" in header
    assert "cost" in header


def test_render_row_returns_string(renderer):
    row = {"price": "100", "cost": "80", "qty": "5"}
    result = renderer.render_row(row)
    assert isinstance(result, str)


def test_render_row_diff_positive(renderer):
    row = {"price": "100", "cost": "80", "qty": "5"}
    result = renderer.render_row(row)
    assert "+20" in result


def test_render_row_diff_negative(renderer):
    row = {"price": "50", "cost": "80", "qty": "5"}
    result = renderer.render_row(row)
    assert "-30" in result


def test_render_all_returns_string(renderer):
    rows = [
        {"price": "10", "cost": "8", "qty": "1"},
        {"price": "20", "cost": "25", "qty": "2"},
    ]
    out = renderer.render_all(rows)
    assert isinstance(out, str)
    assert out.count("\n") >= 2


def test_render_row_no_rules_empty():
    e = ColumnCompareEngine(["a", "b"])
    r = ColumnCompareRenderer(e, col_width=8)
    result = r.render_row({"a": "1", "b": "2"})
    assert result == ""
