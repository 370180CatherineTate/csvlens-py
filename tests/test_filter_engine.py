"""Tests for the FilterEngine module."""

import pytest
from csvlens.filter_engine import FilterEngine


HEADERS = ["name", "city", "age", "email"]

ROWS = [
    ["Alice", "New York", "30", "alice@example.com"],
    ["Bob", "Boston", "25", "bob@work.org"],
    ["Charlie", "New York", "35", "charlie@example.com"],
    ["Diana", "Chicago", "", "diana@sample.net"],
    ["Eve", "Boston", "28", "eve@example.com"],
]


@pytest.fixture
def engine():
    return FilterEngine(HEADERS)


def test_no_filters_returns_all(engine):
    result = engine.apply(ROWS)
    assert result == ROWS


def test_global_filter_matches_any_column(engine):
    engine.set_global_filter("boston")
    result = engine.apply(ROWS)
    assert len(result) == 2
    assert all(row[1] == "Boston" for row in result)


def test_global_filter_case_sensitive(engine):
    engine.set_global_filter("boston", case_sensitive=True)
    result = engine.apply(ROWS)
    assert result == []


def test_column_filter_specific_column(engine):
    engine.set_column_filter("city", "new york")
    result = engine.apply(ROWS)
    assert len(result) == 2
    assert all(row[1] == "New York" for row in result)


def test_column_filter_email_domain(engine):
    engine.set_column_filter("email", r"@example\.com")
    result = engine.apply(ROWS)
    assert len(result) == 3


def test_combined_global_and_column_filter(engine):
    engine.set_global_filter("example.com")
    engine.set_column_filter("city", "new york")
    result = engine.apply(ROWS)
    assert len(result) == 1
    assert result[0][0] == "Charlie"


def test_clear_filters(engine):
    engine.set_global_filter("boston")
    engine.clear_filters()
    result = engine.apply(ROWS)
    assert result == ROWS


def test_invalid_column_raises(engine):
    with pytest.raises(ValueError, match="not found in headers"):
        engine.set_column_filter("nonexistent", "value")


def test_active_filters_summary(engine):
    engine.set_global_filter("test")
    engine.set_column_filter("city", "boston")
    active = engine.active_filters
    assert "__global__" in active
    assert "city" in active
    assert active["__global__"] == "test"


def test_iter_apply_lazy(engine):
    engine.set_column_filter("city", "boston")
    result = list(engine.iter_apply(iter(ROWS)))
    assert len(result) == 2


def test_matches_empty_cell_gracefully(engine):
    engine.set_column_filter("age", r"\d+")
    result = engine.apply(ROWS)
    assert all(row[2] != "" for row in result)
    assert len(result) == 4
