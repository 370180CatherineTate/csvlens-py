"""Tests for ColumnWidthProfile."""

import pytest

from csvlens.column_width_profile import ColumnWidthProfile


@pytest.fixture()
def rows():
    return [
        {"name": "Alice", "age": "30", "city": "New York"},
        {"name": "Bob", "age": "4", "city": "LA"},
        {"name": "Charlotte", "age": "25", "city": "San Francisco"},
    ]


@pytest.fixture()
def profile(rows):
    return ColumnWidthProfile(["name", "age", "city"], rows)


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers"):
        ColumnWidthProfile([], [])


def test_min_width_less_than_one_raises(rows):
    with pytest.raises(ValueError, match="min_width"):
        ColumnWidthProfile(["name"], rows, min_width=0)


def test_max_less_than_min_raises(rows):
    with pytest.raises(ValueError, match="max_width"):
        ColumnWidthProfile(["name"], rows, min_width=10, max_width=5)


def test_headers_property(profile):
    assert profile.headers == ["name", "age", "city"]


def test_min_max_defaults(profile):
    assert profile.min_width == ColumnWidthProfile.MIN_WIDTH
    assert profile.max_width == ColumnWidthProfile.MAX_WIDTH


def test_width_for_uses_longest_value(profile):
    # "Charlotte" is 9 chars, header "name" is 4
    assert profile.width_for("name") == len("Charlotte")


def test_width_for_header_baseline(profile):
    # "age" header len=3, values "30","4","25" max=2 → header wins → 3
    assert profile.width_for("age") == len("age")


def test_width_for_city(profile):
    # "San Francisco" = 13 chars
    assert profile.width_for("city") == len("San Francisco")


def test_width_capped_at_max():
    long_val = "x" * 200
    rows = [{"col": long_val}]
    p = ColumnWidthProfile(["col"], rows, max_width=20)
    assert p.width_for("col") == 20


def test_width_floored_at_min():
    rows = [{"c": "x"}]
    p = ColumnWidthProfile(["c"], rows, min_width=10)
    assert p.width_for("c") == 10


def test_unknown_column_raises(profile):
    with pytest.raises(KeyError):
        profile.width_for("nonexistent")


def test_all_widths_returns_dict(profile):
    w = profile.all_widths()
    assert isinstance(w, dict)
    assert set(w.keys()) == {"name", "age", "city"}


def test_all_widths_values_match_width_for(profile):
    """all_widths() values should be consistent with individual width_for() calls."""
    w = profile.all_widths()
    for header in profile.headers:
        assert w[header] == profile.width_for(header)


def test_sample_size_limits_rows():
    rows = [
        {"val": "short"},
        {"val": "a very long value indeed"},
    ]
    p = ColumnWidthProfile(["val"], rows, sample_size=1)
    # Only first row sampled; "short" < header "val" len=3 → min_width=3
    assert p.width_for("val") == len("short")


def test_empty_rows_uses_header_width():
    p = ColumnWidthProfile(["column"], [])
    assert p.width_for("column") == len("column")
