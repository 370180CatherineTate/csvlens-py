"""Tests for ColumnPinEngine."""

import pytest
from csvlens.column_pin_engine import ColumnPinEngine


@pytest.fixture
def engine() -> ColumnPinEngine:
    return ColumnPinEngine(["id", "name", "age", "city"])


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnPinEngine([])


def test_headers_property(engine):
    assert engine.headers == ["id", "name", "age", "city"]


def test_initial_no_pinned(engine):
    assert engine.pinned == []


def test_initial_all_unpinned(engine):
    assert engine.unpinned == ["id", "name", "age", "city"]


def test_ordered_no_pins_matches_original(engine):
    assert engine.ordered == ["id", "name", "age", "city"]


def test_pin_single_column(engine):
    engine.pin("city")
    assert engine.pinned == ["city"]
    assert "city" not in engine.unpinned


def test_ordered_pinned_first(engine):
    engine.pin("city")
    assert engine.ordered == ["city", "id", "name", "age"]


def test_pin_multiple_preserves_pin_order(engine):
    engine.pin("age")
    engine.pin("id")
    assert engine.pinned == ["age", "id"]
    assert engine.ordered == ["age", "id", "name", "city"]


def test_pin_unknown_column_raises(engine):
    with pytest.raises(ValueError, match="Unknown column"):
        engine.pin("salary")


def test_pin_already_pinned_raises(engine):
    engine.pin("name")
    with pytest.raises(ValueError, match="already pinned"):
        engine.pin("name")


def test_unpin_column(engine):
    engine.pin("name")
    engine.unpin("name")
    assert engine.pinned == []
    assert engine.unpinned == ["id", "name", "age", "city"]


def test_unpin_not_pinned_raises(engine):
    with pytest.raises(ValueError, match="not pinned"):
        engine.unpin("age")


def test_unpin_all(engine):
    engine.pin("id")
    engine.pin("city")
    engine.unpin_all()
    assert engine.pinned == []
    assert len(engine.unpinned) == 4


def test_is_pinned_true(engine):
    engine.pin("name")
    assert engine.is_pinned("name") is True


def test_is_pinned_false(engine):
    assert engine.is_pinned("name") is False


def test_reorder_row(engine):
    engine.pin("city")
    row = {"id": "1", "name": "Alice", "age": "30", "city": "Paris"}
    reordered = engine.reorder_row(row)
    assert list(reordered.keys()) == ["city", "id", "name", "age"]
    assert reordered["city"] == "Paris"


def test_reorder_row_no_pins_preserves_order(engine):
    row = {"id": "1", "name": "Bob", "age": "25", "city": "Rome"}
    reordered = engine.reorder_row(row)
    assert list(reordered.keys()) == ["id", "name", "age", "city"]
