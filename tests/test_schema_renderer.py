"""Tests for SchemaRenderer."""

import pytest
from csvlens.schema_inspector import SchemaInspector
from csvlens.schema_renderer import SchemaRenderer


@pytest.fixture
def inspector():
    headers = ["id", "name", "price"]
    rows = [
        {"id": "1", "name": "apple", "price": "1.99"},
        {"id": "2", "name": "banana", "price": "0.50"},
    ]
    return SchemaInspector(headers, rows)


@pytest.fixture
def renderer(inspector):
    return SchemaRenderer(inspector, use_color=False)


def test_invalid_col_width_raises(inspector):
    with pytest.raises(ValueError, match="col_width"):
        SchemaRenderer(inspector, col_width=2)


def test_render_returns_string(renderer):
    result = renderer.render()
    assert isinstance(result, str)


def test_render_contains_column_header(renderer):
    result = renderer.render()
    assert "COLUMN" in result


def test_render_contains_type_header(renderer):
    result = renderer.render()
    assert "TYPE" in result


def test_render_contains_all_columns(renderer):
    result = renderer.render()
    assert "id" in result
    assert "name" in result
    assert "price" in result


def test_render_contains_inferred_types(renderer):
    result = renderer.render()
    assert "integer" in result
    assert "string" in result
    assert "float" in result


def test_render_has_separator_line(renderer):
    lines = renderer.render().splitlines()
    assert any(set(line.strip()) == {"-"} for line in lines)


def test_render_str_equals_render(renderer):
    assert renderer.render_str() == renderer.render()


def test_render_with_color_contains_ansi(inspector):
    r = SchemaRenderer(inspector, use_color=True)
    result = r.render()
    assert "\033[" in result


def test_render_without_color_no_ansi(renderer):
    result = renderer.render()
    assert "\033[" not in result


def test_col_width_truncates_long_names():
    headers = ["a_very_long_column_name_here"]
    rows = [{"a_very_long_column_name_here": "42"}]
    ins = SchemaInspector(headers, rows)
    r = SchemaRenderer(ins, use_color=False, col_width=10)
    result = r.render()
    assert "a_very_lon" in result
    assert "a_very_long_column_name_here" not in result
