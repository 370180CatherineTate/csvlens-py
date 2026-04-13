"""Tests for JumpEngine."""

import pytest

from csvlens.jump_engine import JumpEngine


@pytest.fixture
def engine() -> JumpEngine:
    bookmarks = {"top": 0, "middle": 49, "last": 99}
    return JumpEngine(total_rows=100, bookmarks=bookmarks)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_negative_total_rows_raises():
    with pytest.raises(ValueError, match="total_rows"):
        JumpEngine(total_rows=-1)


def test_zero_total_rows_allowed():
    e = JumpEngine(total_rows=0)
    assert e.total_rows == 0


def test_default_no_bookmarks():
    e = JumpEngine(total_rows=10)
    assert e.bookmark_names == []


# ---------------------------------------------------------------------------
# jump_to_row
# ---------------------------------------------------------------------------

def test_jump_to_row_first(engine):
    assert engine.jump_to_row(1) == 0


def test_jump_to_row_last(engine):
    assert engine.jump_to_row(100) == 99


def test_jump_to_row_middle(engine):
    assert engine.jump_to_row(50) == 49


def test_jump_to_row_zero_raises(engine):
    with pytest.raises(ValueError, match="out of range"):
        engine.jump_to_row(0)


def test_jump_to_row_exceeds_total_raises(engine):
    with pytest.raises(ValueError, match="out of range"):
        engine.jump_to_row(101)


def test_jump_to_row_empty_dataset_raises():
    e = JumpEngine(total_rows=0)
    with pytest.raises(ValueError, match="empty"):
        e.jump_to_row(1)


# ---------------------------------------------------------------------------
# jump_to_bookmark
# ---------------------------------------------------------------------------

def test_jump_to_known_bookmark(engine):
    assert engine.jump_to_bookmark("top") == 0
    assert engine.jump_to_bookmark("middle") == 49
    assert engine.jump_to_bookmark("last") == 99


def test_jump_to_unknown_bookmark_raises(engine):
    with pytest.raises(KeyError, match="unknown"):
        engine.jump_to_bookmark("unknown")


# ---------------------------------------------------------------------------
# resolve
# ---------------------------------------------------------------------------

def test_resolve_numeric_string(engine):
    assert engine.resolve("1") == 0
    assert engine.resolve("100") == 99


def test_resolve_bookmark_name(engine):
    assert engine.resolve("top") == 0
    assert engine.resolve("middle") == 49


def test_resolve_whitespace_stripped(engine):
    assert engine.resolve("  10  ") == 9


def test_resolve_unknown_target_raises(engine):
    with pytest.raises(ValueError, match="Cannot resolve"):
        engine.resolve("nowhere")


def test_resolve_out_of_range_numeric_raises(engine):
    with pytest.raises(ValueError):
        engine.resolve("999")
