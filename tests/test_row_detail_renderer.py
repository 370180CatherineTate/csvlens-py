"""Tests for RowDetailRenderer."""

import pytest

from csvlens.row_detail_renderer import RowDetailRenderer


HEADERS = ["id", "name", "age", "city"]
ROW = ["1", "Alice", "30", "London"]


@pytest.fixture
def renderer() -> RowDetailRenderer:
    return RowDetailRenderer(HEADERS, col_width=10, colorize=False)


# ---------------------------------------------------------------------------
# Construction errors
# ---------------------------------------------------------------------------

def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        RowDetailRenderer([])


def test_invalid_col_width_raises():
    with pytest.raises(ValueError, match="col_width must be >= 1"):
        RowDetailRenderer(HEADERS, col_width=0)


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------

def test_headers_property(renderer):
    assert renderer.headers == HEADERS


def test_col_width_property(renderer):
    assert renderer.col_width == 10


def test_headers_returns_copy(renderer):
    copy = renderer.headers
    copy.append("extra")
    assert renderer.headers == HEADERS


# ---------------------------------------------------------------------------
# render() basic behaviour
# ---------------------------------------------------------------------------

def test_render_returns_string(renderer):
    result = renderer.render(ROW)
    assert isinstance(result, str)


def test_render_contains_all_headers(renderer):
    result = renderer.render(ROW)
    for header in HEADERS:
        assert header in result


def test_render_contains_all_values(renderer):
    result = renderer.render(ROW)
    for value in ROW:
        assert value in result


def test_render_with_row_index(renderer):
    result = renderer.render(ROW, row_index=5)
    assert "Row 5" in result


def test_render_without_row_index_shows_default(renderer):
    result = renderer.render(ROW)
    assert "Row detail" in result


def test_render_mismatched_row_raises(renderer):
    with pytest.raises(ValueError, match="row has 2 columns"):
        renderer.render(["1", "Alice"])


# ---------------------------------------------------------------------------
# Colorize flag
# ---------------------------------------------------------------------------

def test_colorize_false_no_ansi(renderer):
    result = renderer.render(ROW)
    assert "\033[" not in result


def test_colorize_true_includes_ansi():
    r = RowDetailRenderer(HEADERS, col_width=10, colorize=True)
    result = r.render(ROW)
    assert "\033[" in result


# ---------------------------------------------------------------------------
# Separator line
# ---------------------------------------------------------------------------

def test_render_includes_separator(renderer):
    result = renderer.render(ROW)
    assert "---" in result


# ---------------------------------------------------------------------------
# Key-value separator
# ---------------------------------------------------------------------------

def test_render_key_value_separator(renderer):
    result = renderer.render(ROW)
    # Each header should appear with " : " separator
    assert " : " in result
