"""Tests for ColumnAggregateRenderer."""
import pytest

from csvlens.column_aggregate_engine import ColumnAggregateEngine
from csvlens.column_aggregate_renderer import ColumnAggregateRenderer


@pytest.fixture
def rows():
    return [
        {"price": "10.0", "qty": "3", "label": "apple"},
        {"price": "20.0", "qty": "5", "label": "banana"},
        {"price": "15.0", "qty": "",  "label": "cherry"},
    ]


@pytest.fixture
def renderer(rows):
    eng = ColumnAggregateEngine(["price", "qty", "label"])
    eng.compute(rows)
    return ColumnAggregateRenderer(eng)


def test_invalid_col_width_raises(rows):
    eng = ColumnAggregateEngine(["price"])
    eng.compute(rows)
    with pytest.raises(ValueError):
        ColumnAggregateRenderer(eng, col_width=3)


def test_col_width_property(renderer):
    assert renderer.col_width == 14


def test_render_returns_string(renderer):
    result = renderer.render()
    assert isinstance(result, str)


def test_render_contains_column_names(renderer):
    result = renderer.render()
    assert "price" in result
    assert "qty" in result
    assert "label" in result


def test_render_contains_aggregate_labels(renderer):
    result = renderer.render()
    for label in ["sum", "mean", "min", "max", "count"]:
        assert label in result


def test_render_dash_for_non_numeric(renderer):
    result = renderer.render()
    assert "—" in result


def test_render_multiline(renderer):
    lines = renderer.render().splitlines()
    # header + separator + 5 aggregate rows
    assert len(lines) >= 7


def test_custom_col_width(rows):
    eng = ColumnAggregateEngine(["price"])
    eng.compute(rows)
    r = ColumnAggregateRenderer(eng, col_width=10)
    assert r.col_width == 10
    out = r.render()
    assert isinstance(out, str)
