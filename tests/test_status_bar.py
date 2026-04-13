"""Tests for csvlens.status_bar.StatusBar."""

import pytest

from csvlens.status_bar import StatusBar


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_bar(**kwargs) -> StatusBar:
    defaults = dict(
        total_rows=100,
        visible_rows=100,
        current_page=1,
        total_pages=5,
    )
    defaults.update(kwargs)
    return StatusBar(**defaults)


# ---------------------------------------------------------------------------
# Construction guards
# ---------------------------------------------------------------------------

def test_negative_total_rows_raises():
    with pytest.raises(ValueError, match="total_rows"):
        make_bar(total_rows=-1)


def test_total_pages_less_than_one_raises():
    with pytest.raises(ValueError, match="total_pages"):
        make_bar(total_pages=0)


def test_current_page_out_of_range_raises():
    with pytest.raises(ValueError, match="current_page"):
        make_bar(current_page=0)


def test_current_page_exceeds_total_pages_raises():
    with pytest.raises(ValueError, match="current_page"):
        make_bar(current_page=6, total_pages=5)


def test_visible_rows_exceeds_total_rows_raises():
    with pytest.raises(ValueError, match="visible_rows"):
        make_bar(visible_rows=150, total_rows=100)


# ---------------------------------------------------------------------------
# Render content
# ---------------------------------------------------------------------------

def test_render_contains_row_summary():
    bar = make_bar(total_rows=200, visible_rows=50)
    result = bar.render()
    assert "50/200" in result


def test_render_contains_page_summary():
    bar = make_bar(current_page=3, total_pages=10)
    result = bar.render()
    assert "3/10" in result


def test_render_no_sort_by_default():
    bar = make_bar()
    assert "Sort" not in bar.render()


def test_render_sort_ascending():
    bar = make_bar(sort_column="age", sort_ascending=True)
    result = bar.render()
    assert "Sort: age" in result
    assert "\u25b2" in result  # up arrow


def test_render_sort_descending():
    bar = make_bar(sort_column="name", sort_ascending=False)
    result = bar.render()
    assert "\u25bc" in result  # down arrow


def test_render_global_filter_shown():
    bar = make_bar(global_filter="alice")
    result = bar.render()
    assert "Filter:" in result
    assert "alice" in result


def test_render_no_filter_by_default():
    bar = make_bar()
    assert "Filter" not in bar.render()


def test_render_frozen_count_shown():
    bar = make_bar(frozen_count=2)
    assert "Frozen: 2" in bar.render()


def test_render_frozen_zero_hidden():
    bar = make_bar(frozen_count=0)
    assert "Frozen" not in bar.render()


def test_render_search_with_matches():
    bar = make_bar(
        search_pattern="foo",
        current_match=2,
        total_matches=5,
    )
    result = bar.render()
    assert "Search:" in result
    assert "2/5" in result


def test_render_search_no_matches():
    bar = make_bar(search_pattern="xyz", total_matches=0)
