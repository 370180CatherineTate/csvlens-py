"""Tests for MultiSortEngine."""
import pytest

from csvlens.column_sort_profile import ColumnSortProfile
from csvlens.multi_sort_engine import MultiSortEngine

HEADERS = ["name", "age", "city"]

ROWS = [
    {"name": "Alice", "age": "30", "city": "Boston"},
    {"name": "Bob", "age": "25", "city": "Austin"},
    {"name": "Carol", "age": "30", "city": "Austin"},
    {"name": "Dave", "age": "20", "city": "Boston"},
]


@pytest.fixture
def engine():
    profile = ColumnSortProfile(HEADERS)
    return MultiSortEngine(profile)


@pytest.fixture
def profile():
    return ColumnSortProfile(HEADERS)


def test_headers_property(engine):
    assert engine.headers == HEADERS


def test_no_active_profile_preserves_order(engine):
    result = engine.sort(ROWS)
    assert [r["name"] for r in result] == ["Alice", "Bob", "Carol", "Dave"]


def test_sort_single_column_ascending(profile):
    profile.save("by_age_asc", [("age", True)])
    profile.activate("by_age_asc")
    eng = MultiSortEngine(profile)
    result = eng.sort(ROWS)
    ages = [int(r["age"]) for r in result]
    assert ages == sorted(ages)


def test_sort_single_column_descending(profile):
    profile.save("by_age_desc", [("age", False)])
    profile.activate("by_age_desc")
    eng = MultiSortEngine(profile)
    result = eng.sort(ROWS)
    ages = [int(r["age"]) for r in result]
    assert ages == sorted(ages, reverse=True)


def test_sort_multi_column(profile):
    profile.save("age_then_name", [("age", True), ("name", True)])
    profile.activate("age_then_name")
    eng = MultiSortEngine(profile)
    result = eng.sort(ROWS)
    # Dave(20), Bob(25), Alice(30), Carol(30)
    assert result[0]["name"] == "Dave"
    assert result[1]["name"] == "Bob"
    # Alice and Carol both age=30, sorted by name asc
    assert result[2]["name"] == "Alice"
    assert result[3]["name"] == "Carol"


def test_sort_returns_copy_not_mutate(profile):
    profile.save("by_age", [("age", True)])
    profile.activate("by_age")
    eng = MultiSortEngine(profile)
    original = list(ROWS)
    result = eng.sort(ROWS)
    assert ROWS == original  # original unchanged
    assert result is not ROWS


def test_sort_missing_column_value_handled(profile):
    rows = [{"name": "X", "age": "", "city": "Z"}, {"name": "Y", "age": "5", "city": "A"}]
    profile.save("by_age", [("age", True)])
    profile.activate("by_age")
    eng = MultiSortEngine(profile)
    result = eng.sort(rows)  # should not raise
    assert len(result) == 2


def test_active_profile_property(profile):
    profile.save("p", [("name", True)])
    profile.activate("p")
    eng = MultiSortEngine(profile)
    assert eng.active_profile == "p"
