"""Tests for ColumnHistogram."""

from __future__ import annotations

import pytest

from csvlens.column_histogram import ColumnHistogram, BARS


@pytest.fixture()
def rows():
    return [
        {"age": "10", "name": "alice"},
        {"age": "20", "name": "bob"},
        {"age": "30", "name": "carol"},
        {"age": "40", "name": "dave"},
        {"age": "50", "name": "eve"},
        {"age": "60", "name": "frank"},
        {"age": "70", "name": "grace"},
        {"age": "80", "name": "heidi"},
    ]


@pytest.fixture()
def hist(rows):
    return ColumnHistogram(["age", "name"], rows, num_bins=8)


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnHistogram([], [])


def test_num_bins_too_small_raises():
    with pytest.raises(ValueError, match="num_bins must be at least 2"):
        ColumnHistogram(["a"], [], num_bins=1)


def test_headers_property(hist):
    assert hist.headers == ["age", "name"]


def test_headers_returns_copy(hist):
    h = hist.headers
    h.append("extra")
    assert "extra" not in hist.headers


def test_num_bins_property(hist):
    assert hist.num_bins == 8


def test_render_unknown_column_raises(hist):
    with pytest.raises(KeyError, match="Unknown column"):
        hist.render("salary")


def test_render_numeric_column_length(hist):
    bar = hist.render("age")
    assert len(bar) == 8


def test_render_uses_valid_bar_chars(hist):
    bar = hist.render("age")
    for ch in bar:
        assert ch in BARS


def test_render_non_numeric_column_returns_empty(hist):
    bar = hist.render("name")
    assert bar == ""


def test_render_cached(hist):
    bar1 = hist.render("age")
    bar2 = hist.render("age")
    assert bar1 == bar2


def test_render_all_same_value():
    rows = [{"x": "5"} for _ in range(10)]
    h = ColumnHistogram(["x"], rows, num_bins=4)
    bar = h.render("x")
    assert bar == BARS[-1] * 4


def test_summary_unknown_column_raises(hist):
    with pytest.raises(KeyError):
        hist.summary("salary")


def test_summary_numeric_column(hist):
    s = hist.summary("age")
    assert s["min"] == 10.0
    assert s["max"] == 80.0
    assert abs(s["mean"] - 45.0) < 1e-6
    assert len(s["bar"]) == 8


def test_summary_non_numeric_column(hist):
    s = hist.summary("name")
    assert s["min"] is None
    assert s["max"] is None
    assert s["mean"] is None
    assert s["bar"] == ""


def test_summary_empty_rows():
    h = ColumnHistogram(["x"], [], num_bins=4)
    s = h.summary("x")
    assert s == {"min": None, "max": None, "mean": None, "bar": ""}


def test_render_with_nulls():
    rows = [{"v": "1"}, {"v": ""}, {"v": "bad"}, {"v": "2"}, {"v": "3"}]
    h = ColumnHistogram(["v"], rows, num_bins=4)
    bar = h.render("v")
    assert len(bar) == 4
    for ch in bar:
        assert ch in BARS
