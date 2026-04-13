"""Tests for csvlens.search_engine.SearchEngine."""

import pytest
from csvlens.search_engine import SearchEngine


ROWS = [
    {"name": "Alice", "city": "Amsterdam", "score": "95"},
    {"name": "Bob", "city": "Berlin", "score": "80"},
    {"name": "charlie", "city": "Chicago", "score": "72"},
    {"name": "Diana", "city": "Dublin", "score": "88"},
]


@pytest.fixture
def engine() -> SearchEngine:
    return SearchEngine()


def test_default_state(engine):
    assert engine.pattern == ""
    assert not engine.is_active()


def test_set_pattern_activates(engine):
    engine.set_pattern("alice")
    assert engine.is_active()
    assert engine.pattern == "alice"


def test_clear_deactivates(engine):
    engine.set_pattern("alice")
    engine.clear()
    assert not engine.is_active()


def test_match_row_case_insensitive(engine):
    engine.set_pattern("alice", case_sensitive=False)
    assert engine.match_row(ROWS[0]) is True
    assert engine.match_row(ROWS[1]) is False


def test_match_row_case_sensitive(engine):
    engine.set_pattern("alice", case_sensitive=True)
    assert engine.match_row(ROWS[0]) is False  # 'Alice' != 'alice'
    engine.set_pattern("Alice", case_sensitive=True)
    assert engine.match_row(ROWS[0]) is True


def test_no_pattern_matches_all(engine):
    assert all(engine.match_row(r) for r in ROWS)


def test_filter_rows(engine):
    engine.set_pattern("b")
    result = engine.filter_rows(ROWS)
    names = [r["name"] for r in result]
    assert "Bob" in names
    assert "Berlin" or "Bob" in [r["city"] for r in result]


def test_filter_rows_no_pattern(engine):
    assert engine.filter_rows(ROWS) == ROWS


def test_find_matches_in_row(engine):
    engine.set_pattern("a", case_sensitive=False)
    matches = engine.find_matches_in_row(ROWS[0])  # Alice, Amsterdam
    cols = [col for col, _ in matches]
    assert "name" in cols
    assert "city" in cols


def test_find_matches_returns_correct_spans(engine):
    engine.set_pattern("li", case_sensitive=False)
    row = {"name": "Alice", "city": "Berlin"}
    matches = dict(engine.find_matches_in_row(row))
    assert "name" in matches
    # 'Alice' -> 'li' starts at index 1
    assert matches["name"] == [(1, 3)]


def test_find_matches_in_row_multiple_occurrences(engine):
    """Each occurrence of the pattern within a cell value should be reported."""
    engine.set_pattern("a", case_sensitive=False)
    row = {"name": "banana", "city": "Oslo"}
    matches = dict(engine.find_matches_in_row(row))
    # 'banana' contains 'a' at indices 1, 3, 5
    assert "name" in matches
    assert matches["name"] == [(1, 2), (3, 4), (5, 6)]
    # 'Oslo' contains no 'a'
    assert "city" not in matches


def test_empty_pattern_after_set(engine):
    engine.set_pattern("")
    assert not engine.is_active()
