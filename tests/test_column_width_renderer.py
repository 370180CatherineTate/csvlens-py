"""Tests for ColumnWidthRenderer."""

import pytest

from csvlens.column_width_profile import ColumnWidthProfile
from csvlens.column_width_renderer import ColumnWidthRenderer


@pytest.fixture()
def rows():
    return [
        {"name": "Alice", "score": "100", "city": "Rome"},
        {"name": "Bob", "score": "42", "city": "Paris"},
    ]


@pytest.fixture()
def renderer(rows):
    profile = ColumnWidthProfile(["name", "score", "city"], rows)
    return ColumnWidthRenderer(profile)


def test_render_header_returns_string(renderer):
    h = renderer.render_header()
    assert isinstance(h, str)


def test_render_header_contains_columns(renderer):
    h = renderer.render_header()
    assert "name" in h
    assert "score" in h
    assert "city" in h


def test_render_row_returns_string(renderer, rows):
    line = renderer.render_row(rows[0])
    assert isinstance(line, str)
    assert "Alice" in line


def test_render_row_missing_key_treated_as_empty(renderer):
    line = renderer.render_row({"name": "X"})
    assert isinstance(line, str)


def test_render_all_line_count(renderer, rows):
    output = renderer.render_all(rows)
    lines = output.splitlines()
    # 1 header + 2 data rows
    assert len(lines) == 3


def test_render_all_first_line_is_header(renderer, rows):
    output = renderer.render_all(rows)
    first = output.splitlines()[0]
    assert "name" in first


def test_columns_padded_to_same_width(renderer, rows):
    """All cells in a column should occupy the same character width."""
    header_line = renderer.render_header()
    data_line = renderer.render_row(rows[0])
    # Split on double-space separator and compare field lengths
    sep = ColumnWidthRenderer.SEPARATOR
    h_parts = header_line.split(sep)
    d_parts = data_line.split(sep)
    assert len(h_parts) == len(d_parts)
    for h_cell, d_cell in zip(h_parts, d_parts):
        assert len(h_cell) == len(d_cell)


def test_long_value_truncated():
    long_val = "A" * 100
    rows = [{"col": long_val}]
    profile = ColumnWidthProfile(["col"], rows, max_width=10)
    r = ColumnWidthRenderer(profile)
    cell = r.render_row(rows[0])
    assert len(cell) == 10
    assert cell.endswith("…")


def test_render_all_empty_rows(renderer):
    output = renderer.render_all([])
    lines = output.splitlines()
    assert len(lines) == 1  # only header
