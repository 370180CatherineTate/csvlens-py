"""Tests for BookmarkManager and BookmarkRenderer."""

import pytest

from csvlens.bookmark_manager import BookmarkManager
from csvlens.bookmark_renderer import BookmarkRenderer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def manager() -> BookmarkManager:
    return BookmarkManager(total_rows=100)


# ---------------------------------------------------------------------------
# BookmarkManager – construction
# ---------------------------------------------------------------------------

def test_negative_total_rows_raises():
    with pytest.raises(ValueError):
        BookmarkManager(total_rows=-1)


def test_empty_on_init(manager):
    assert len(manager) == 0
    assert manager.names == []


# ---------------------------------------------------------------------------
# BookmarkManager – add
# ---------------------------------------------------------------------------

def test_add_bookmark(manager):
    manager.add("start", 0)
    assert "start" in manager
    assert manager.get("start") == 0


def test_add_overwrites_existing(manager):
    manager.add("mark", 10)
    manager.add("mark", 20)
    assert manager.get("mark") == 20
    assert len(manager) == 1


def test_add_empty_name_raises(manager):
    with pytest.raises(ValueError):
        manager.add("", 5)


def test_add_whitespace_name_raises(manager):
    with pytest.raises(ValueError):
        manager.add("   ", 5)


def test_add_out_of_range_raises(manager):
    with pytest.raises(IndexError):
        manager.add("bad", 100)  # valid range: 0–99


def test_add_negative_row_raises(manager):
    with pytest.raises(IndexError):
        manager.add("neg", -1)


# ---------------------------------------------------------------------------
# BookmarkManager – remove / clear
# ---------------------------------------------------------------------------

def test_remove_existing(manager):
    manager.add("x", 5)
    manager.remove("x")
    assert "x" not in manager


def test_remove_nonexistent_raises(manager):
    with pytest.raises(KeyError):
        manager.remove("ghost")


def test_clear_removes_all(manager):
    manager.add("a", 1)
    manager.add("b", 2)
    manager.clear()
    assert len(manager) == 0


# ---------------------------------------------------------------------------
# BookmarkManager – all / get
# ---------------------------------------------------------------------------

def test_all_returns_copy(manager):
    manager.add("p", 3)
    copy = manager.all()
    copy["p"] = 99
    assert manager.get("p") == 3


def test_get_missing_returns_none(manager):
    assert manager.get("missing") is None


# ---------------------------------------------------------------------------
# BookmarkRenderer
# ---------------------------------------------------------------------------

def test_render_empty_manager():
    mgr = BookmarkManager(total_rows=10)
    renderer = BookmarkRenderer(mgr)
    lines = renderer.render()
    assert lines == ["No bookmarks saved."]


def test_render_contains_bookmark_name():
    mgr = BookmarkManager(total_rows=50)
    mgr.add("chapter1", 12)
    renderer = BookmarkRenderer(mgr)
    output = renderer.render_str()
    assert "chapter1" in output
    assert "12" in output


def test_render_includes_header_and_borders():
    mgr = BookmarkManager(total_rows=50)
    mgr.add("foo", 7)
    lines = BookmarkRenderer(mgr).render()
    # separator, header, separator, data row, separator
    assert len(lines) == 5
    assert lines[0].startswith("+")
    assert "Name" in lines[1]
    assert "Row" in lines[1]
