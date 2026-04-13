"""Tests for RowFilterHistory and FilterSnapshot."""

import pytest
from csvlens.row_filter_history import FilterSnapshot, RowFilterHistory


# ---------------------------------------------------------------------------
# FilterSnapshot tests
# ---------------------------------------------------------------------------

def test_snapshot_empty_by_default():
    s = FilterSnapshot()
    assert s.is_empty()


def test_snapshot_not_empty_with_global():
    s = FilterSnapshot(global_filter="foo")
    assert not s.is_empty()


def test_snapshot_description_global_only():
    s = FilterSnapshot(global_filter="hello")
    assert "global='hello'" in s.description()


def test_snapshot_description_column_only():
    s = FilterSnapshot(column_filter=("name", "alice"))
    assert "column='name'" in s.description()
    assert "'alice'" in s.description()


def test_snapshot_description_both():
    s = FilterSnapshot(global_filter="x", column_filter=("age", "30"))
    desc = s.description()
    assert "global=" in desc
    assert "column=" in desc


def test_snapshot_description_empty():
    assert FilterSnapshot().description() == "<empty>"


# ---------------------------------------------------------------------------
# RowFilterHistory construction
# ---------------------------------------------------------------------------

@pytest.fixture
def history():
    return RowFilterHistory(max_size=5)


def test_invalid_max_size_raises():
    with pytest.raises(ValueError):
        RowFilterHistory(max_size=0)


def test_initial_state(history):
    assert history.current is None
    assert not history.can_undo
    assert not history.can_redo


# ---------------------------------------------------------------------------
# push / current
# ---------------------------------------------------------------------------

def test_push_single(history):
    s = FilterSnapshot(global_filter="foo")
    history.push(s)
    assert history.current is s


def test_push_multiple_advances_cursor(history):
    s1 = FilterSnapshot(global_filter="a")
    s2 = FilterSnapshot(global_filter="b")
    history.push(s1)
    history.push(s2)
    assert history.current is s2


def test_push_discards_redo_history(history):
    history.push(FilterSnapshot(global_filter="a"))
    history.push(FilterSnapshot(global_filter="b"))
    history.undo()
    history.push(FilterSnapshot(global_filter="c"))
    assert not history.can_redo


def test_max_size_respected():
    h = RowFilterHistory(max_size=3)
    for i in range(5):
        h.push(FilterSnapshot(global_filter=str(i)))
    assert len(h._stack) == 3
    assert h.current.global_filter == "4"


# ---------------------------------------------------------------------------
# undo / redo
# ---------------------------------------------------------------------------

def test_undo_returns_previous(history):
    s1 = FilterSnapshot(global_filter="first")
    s2 = FilterSnapshot(global_filter="second")
    history.push(s1)
    history.push(s2)
    result = history.undo()
    assert result is s1
    assert history.current is s1


def test_undo_at_start_returns_none(history):
    history.push(FilterSnapshot(global_filter="only"))
    assert history.undo() is None


def test_redo_after_undo(history):
    s1 = FilterSnapshot(global_filter="a")
    s2 = FilterSnapshot(global_filter="b")
    history.push(s1)
    history.push(s2)
    history.undo()
    result = history.redo()
    assert result is s2


def test_redo_at_end_returns_none(history):
    history.push(FilterSnapshot(global_filter="only"))
    assert history.redo() is None


# ---------------------------------------------------------------------------
# clear / history_descriptions
# ---------------------------------------------------------------------------

def test_clear_resets_state(history):
    history.push(FilterSnapshot(global_filter="x"))
    history.clear()
    assert history.current is None
    assert not history.can_undo
    assert not history.can_redo


def test_history_descriptions(history):
    history.push(FilterSnapshot(global_filter="foo"))
    history.push(FilterSnapshot(column_filter=("city", "NY")))
    descs = history.history_descriptions()
    assert len(descs) == 2
    assert "foo" in descs[0]
    assert "city" in descs[1]
