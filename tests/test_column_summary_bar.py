"""Tests for ColumnSummaryBar."""

import pytest

from csvlens.column_summary_bar import ColumnSummaryBar


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def rows():
    return [
        {"name": "Alice", "age": "30", "score": "88.5"},
        {"name": "Bob",   "age": "25", "score": ""},
        {"name": "Carol", "age": "",   "score": "72.0"},
        {"name": "Alice", "age": "40", "score": "95.0"},
    ]


@pytest.fixture
def bar(rows):
    return ColumnSummaryBar(["name", "age", "score"], rows)


# ---------------------------------------------------------------------------
# construction guards
# ---------------------------------------------------------------------------

def test_empty_headers_raises(rows):
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnSummaryBar([], rows)


def test_col_width_too_small_raises(rows):
    with pytest.raises(ValueError, match="col_width must be >= 4"):
        ColumnSummaryBar(["name"], rows, col_width=3)


# ---------------------------------------------------------------------------
# headers property
# ---------------------------------------------------------------------------

def test_headers_property(bar):
    assert bar.headers == ["name", "age", "score"]


def test_headers_returns_copy(bar):
    h = bar.headers
    h.append("extra")
    assert "extra" not in bar.headers


# ---------------------------------------------------------------------------
# render – basic
# ---------------------------------------------------------------------------

def test_render_returns_string(bar):
    result = bar.render("name", color=False)
    assert isinstance(result, str)


def test_render_unknown_column_raises(bar):
    with pytest.raises(KeyError, match="Unknown column"):
        bar.render("nonexistent", color=False)


def test_render_contains_col_name(bar):
    result = bar.render("name", color=False)
    assert "name" in result


def test_render_contains_type(bar):
    result = bar.render("name", color=False)
    assert "type:" in result


def test_render_contains_null_info(bar):
    result = bar.render("age", color=False)
    assert "null:" in result
    assert "non-null:" in result


def test_render_contains_unique(bar):
    result = bar.render("name", color=False)
    assert "unique:" in result


# ---------------------------------------------------------------------------
# render – numeric extras
# ---------------------------------------------------------------------------

def test_numeric_column_has_min_max_mean(bar):
    result = bar.render("score", color=False)
    assert "min:" in result
    assert "max:" in result
    assert "mean:" in result


def test_string_column_has_no_min_max(bar):
    result = bar.render("name", color=False)
    assert "min:" not in result
    assert "max:" not in result


# ---------------------------------------------------------------------------
# render – color flag
# ---------------------------------------------------------------------------

def test_color_true_contains_ansi(bar):
    result = bar.render("name", color=True)
    assert "\033[" in result


def test_color_false_no_ansi(bar):
    result = bar.render("name", color=False)
    assert "\033[" not in result
