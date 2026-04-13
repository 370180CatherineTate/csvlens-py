"""Tests for FreezeEngine."""

import pytest

from csvlens.freeze_engine import FreezeEngine


HEADERS = ["id", "name", "age", "city", "score"]


@pytest.fixture
def engine() -> FreezeEngine:
    return FreezeEngine(HEADERS)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_empty_headers_raises():
    with pytest.raises(ValueError):
        FreezeEngine([])


def test_initial_state(engine):
    assert engine.frozen == []
    assert engine.frozen_count == 0
    assert engine.unfrozen == HEADERS


def test_headers_property(engine):
    assert engine.headers == HEADERS


# ---------------------------------------------------------------------------
# Freeze / unfreeze
# ---------------------------------------------------------------------------

def test_freeze_single_column(engine):
    engine.freeze("id")
    assert engine.frozen == ["id"]
    assert engine.frozen_count == 1
    assert "id" not in engine.unfrozen


def test_freeze_multiple_columns_preserves_order(engine):
    engine.freeze("city")
    engine.freeze("id")
    assert engine.frozen == ["city", "id"]


def test_freeze_duplicate_is_noop(engine):
    engine.freeze("name")
    engine.freeze("name")
    assert engine.frozen == ["name"]


def test_freeze_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.freeze("nonexistent")


def test_unfreeze_column(engine):
    engine.freeze("id")
    engine.unfreeze("id")
    assert engine.frozen == []
    assert "id" in engine.unfrozen


def test_unfreeze_not_frozen_is_noop(engine):
    engine.unfreeze("age")  # should not raise
    assert engine.frozen == []


def test_unfreeze_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.unfreeze("ghost")


def test_unfreeze_all(engine):
    engine.freeze("id")
    engine.freeze("name")
    engine.unfreeze_all()
    assert engine.frozen == []
    assert engine.unfrozen == HEADERS


def test_is_frozen(engine):
    engine.freeze("score")
    assert engine.is_frozen("score") is True
    assert engine.is_frozen("name") is False


# ---------------------------------------------------------------------------
# Ordered headers & apply
# ---------------------------------------------------------------------------

def test_ordered_headers_frozen_first(engine):
    engine.freeze("score")
    engine.freeze("id")
    result = engine.ordered_headers()
    assert result[:2] == ["score", "id"]
    # remaining columns keep original relative order
    assert result[2:] == ["name", "age", "city"]


def test_ordered_headers_no_frozen(engine):
    assert engine.ordered_headers() == HEADERS


def test_apply_reorders_dict(engine):
    engine.freeze("city")
    row = {"id": 1, "name": "Alice", "age": 30, "city": "NY", "score": 95}
    result = engine.apply(row)
    keys = list(result.keys())
    assert keys[0] == "city"
    assert set(keys) == set(HEADERS)


def test_apply_skips_missing_keys(engine):
    engine.freeze("id")
    row = {"id": 1, "name": "Bob"}  # missing age, city, score
    result = engine.apply(row)
    assert list(result.keys()) == ["id", "name"]
