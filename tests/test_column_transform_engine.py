"""Tests for ColumnTransformEngine."""

import pytest
from csvlens.column_transform_engine import ColumnTransformEngine


HEADERS = ["name", "city", "score"]

SAMPLE_ROWS = [
    {"name": "  Alice  ", "city": "new york", "score": "42"},
    {"name": "BOB", "city": "London", "score": "7"},
]


@pytest.fixture
def engine() -> ColumnTransformEngine:
    return ColumnTransformEngine(HEADERS)


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnTransformEngine([])


def test_headers_property(engine):
    assert engine.headers == HEADERS


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert engine.headers == HEADERS


def test_initial_no_transforms(engine):
    assert engine.transforms == {}


def test_set_transform_upper(engine):
    engine.set_transform("city", "upper")
    assert engine.transforms["city"] == "upper"


def test_set_transform_lower(engine):
    engine.set_transform("name", "lower")
    row = engine.apply_row({"name": "ALICE", "city": "NYC", "score": "1"})
    assert row["name"] == "alice"
    assert row["city"] == "NYC"  # unchanged


def test_set_transform_strip(engine):
    engine.set_transform("name", "strip")
    row = engine.apply_row({"name": "  Alice  ", "city": "NYC", "score": "1"})
    assert row["name"] == "Alice"


def test_set_transform_title(engine):
    engine.set_transform("city", "title")
    row = engine.apply_row({"name": "alice", "city": "new york", "score": "5"})
    assert row["city"] == "New York"


def test_set_transform_unknown_column_raises(engine):
    with pytest.raises(KeyError, match="Unknown column"):
        engine.set_transform("nonexistent", "upper")


def test_set_transform_unknown_name_raises(engine):
    with pytest.raises(ValueError, match="Unknown transform"):
        engine.set_transform("name", "reverse")


def test_set_custom_transform(engine):
    engine.set_custom_transform("score", lambda v: v + "!")
    row = engine.apply_row({"name": "x", "city": "y", "score": "99"})
    assert row["score"] == "99!"
    assert engine.transforms["score"] == "<custom>"


def test_set_custom_transform_not_callable_raises(engine):
    with pytest.raises(TypeError, match="callable"):
        engine.set_custom_transform("name", "not_a_function")  # type: ignore


def test_clear_transform(engine):
    engine.set_transform("city", "upper")
    engine.clear_transform("city")
    assert "city" not in engine.transforms


def test_clear_transform_missing_column_is_noop(engine):
    engine.clear_transform("nonexistent")  # should not raise


def test_clear_all(engine):
    engine.set_transform("name", "lower")
    engine.set_transform("city", "upper")
    engine.clear_all()
    assert engine.transforms == {}


def test_apply_rows(engine):
    engine.set_transform("city", "upper")
    results = engine.apply_rows(SAMPLE_ROWS)
    assert results[0]["city"] == "NEW YORK"
    assert results[1]["city"] == "LONDON"
    # name unchanged
    assert results[0]["name"] == "  Alice  "
