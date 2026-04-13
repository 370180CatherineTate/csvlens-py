"""Tests for DiffEngine."""
import pytest
from csvlens.diff_engine import DiffEngine, DiffResult

HEADERS = ["id", "name", "score"]


@pytest.fixture
def engine():
    return DiffEngine(HEADERS, key_column="id")


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        DiffEngine([])


def test_invalid_key_column_raises():
    with pytest.raises(ValueError, match="key_column"):
        DiffEngine(HEADERS, key_column="nonexistent")


def test_default_key_column_is_first():
    e = DiffEngine(HEADERS)
    assert e.key_column == "id"


def test_headers_property(engine):
    assert engine.headers == HEADERS


def test_no_diff_returns_empty(engine):
    rows = [{"id": "1", "name": "Alice", "score": "90"}]
    result = engine.compute(rows, rows)
    assert not result.has_diff
    assert result.summary == {"added": 0, "removed": 0, "changed": 0}


def test_added_row(engine):
    base = [{"id": "1", "name": "Alice", "score": "90"}]
    curr = [
        {"id": "1", "name": "Alice", "score": "90"},
        {"id": "2", "name": "Bob", "score": "80"},
    ]
    result = engine.compute(base, curr)
    assert len(result.added) == 1
    assert result.added[0]["id"] == "2"
    assert result.removed == []
    assert result.changed == []


def test_removed_row(engine):
    base = [
        {"id": "1", "name": "Alice", "score": "90"},
        {"id": "2", "name": "Bob", "score": "80"},
    ]
    curr = [{"id": "1", "name": "Alice", "score": "90"}]
    result = engine.compute(base, curr)
    assert len(result.removed) == 1
    assert result.removed[0]["id"] == "2"


def test_changed_row(engine):
    base = [{"id": "1", "name": "Alice", "score": "90"}]
    curr = [{"id": "1", "name": "Alice", "score": "95"}]
    result = engine.compute(base, curr)
    assert len(result.changed) == 1
    old, new = result.changed[0]
    assert old["score"] == "90"
    assert new["score"] == "95"


def test_mixed_diff(engine):
    base = [
        {"id": "1", "name": "Alice", "score": "90"},
        {"id": "2", "name": "Bob", "score": "80"},
    ]
    curr = [
        {"id": "1", "name": "Alice", "score": "88"},
        {"id": "3", "name": "Carol", "score": "75"},
    ]
    result = engine.compute(base, curr)
    assert result.summary == {"added": 1, "removed": 1, "changed": 1}
    assert result.has_diff


def test_empty_baseline(engine):
    curr = [{"id": "1", "name": "Alice", "score": "90"}]
    result = engine.compute([], curr)
    assert len(result.added) == 1
    assert result.removed == []


def test_empty_current(engine):
    base = [{"id": "1", "name": "Alice", "score": "90"}]
    result = engine.compute(base, [])
    assert len(result.removed) == 1
    assert result.added == []
