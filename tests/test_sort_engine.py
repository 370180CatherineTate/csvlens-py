"""Tests for csvlens.sort_engine.SortEngine."""

import pytest
from csvlens.sort_engine import SortEngine

HEADERS = ["name", "age", "score"]

ROWS = [
    {"name": "Charlie", "age": "30", "score": "88.5"},
    {"name": "Alice",   "age": "25", "score": "95.0"},
    {"name": "Bob",     "age": "35", "score": "72.0"},
    {"name": "Diana",   "age": "",   "score": "80.0"},
]


@pytest.fixture
def engine() -> SortEngine:
    return SortEngine(HEADERS)


def test_empty_headers_raises():
    with pytest.raises(ValueError):
        SortEngine([])


def test_default_state(engine: SortEngine):
    assert engine.sort_column is None
    assert engine.ascending is True


def test_sort_returns_copy_when_no_sort(engine: SortEngine):
    result = engine.sort(ROWS)
    assert result == ROWS
    assert result is not ROWS


def test_set_sort_invalid_column(engine: SortEngine):
    with pytest.raises(KeyError):
        engine.set_sort("nonexistent")


def test_sort_numeric_ascending(engine: SortEngine):
    engine.set_sort("age", ascending=True)
    result = engine.sort(ROWS)
    ages = [r["age"] for r in result if r["age"] != ""]
    assert ages == sorted(ages, key=float)


def test_sort_numeric_descending(engine: SortEngine):
    engine.set_sort("score", ascending=False)
    result = engine.sort(ROWS)
    scores = [float(r["score"]) for r in result]
    assert scores == sorted(scores, reverse=True)


def test_sort_string_ascending(engine: SortEngine):
    engine.set_sort("name", ascending=True)
    result = engine.sort(ROWS)
    names = [r["name"] for r in result]
    assert names == sorted(names, key=str.lower)


def test_sort_string_descending(engine: SortEngine):
    engine.set_sort("name", ascending=False)
    result = engine.sort(ROWS)
    names = [r["name"] for r in result]
    assert names == sorted(names, key=str.lower, reverse=True)


def test_blank_values_sort_last(engine: SortEngine):
    engine.set_sort("age", ascending=True)
    result = engine.sort(ROWS)
    assert result[-1]["age"] == ""


def test_clear_sort_restores_natural_order(engine: SortEngine):
    engine.set_sort("name")
    engine.clear_sort()
    assert engine.sort_column is None
    assert engine.sort(ROWS) == ROWS


def test_sort_does_not_mutate_input(engine: SortEngine):
    original = [dict(r) for r in ROWS]
    engine.set_sort("score")
    engine.sort(ROWS)
    assert ROWS == original
