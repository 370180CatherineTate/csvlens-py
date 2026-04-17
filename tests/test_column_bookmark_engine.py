import pytest
from csvlens.column_bookmark_engine import ColumnBookmarkEngine


@pytest.fixture
def engine():
    return ColumnBookmarkEngine(["id", "name", "age", "email"])


def test_empty_headers_raises():
    with pytest.raises(ValueError):
        ColumnBookmarkEngine([])


def test_headers_property(engine):
    assert engine.headers == ["id", "name", "age", "email"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


def test_initial_none_bookmarked(engine):
    assert engine.bookmarked == []


def test_initial_all_unbookmarked(engine):
    assert engine.unbookmarked == ["id", "name", "age", "email"]


def test_add_bookmark(engine):
    engine.add("name")
    assert engine.is_bookmarked("name")
    assert "name" in engine.bookmarked


def test_add_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.add("nonexistent")


def test_remove_bookmark(engine):
    engine.add("age")
    engine.remove("age")
    assert not engine.is_bookmarked("age")


def test_remove_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.remove("ghost")


def test_toggle_adds_then_removes(engine):
    result = engine.toggle("id")
    assert result is True
    assert engine.is_bookmarked("id")
    result = engine.toggle("id")
    assert result is False
    assert not engine.is_bookmarked("id")


def test_toggle_unknown_raises(engine):
    with pytest.raises(KeyError):
        engine.toggle("??")


def test_bookmarked_order_preserved(engine):
    engine.add("email")
    engine.add("id")
    assert engine.bookmarked == ["id", "email"]


def test_clear_removes_all(engine):
    engine.add("id")
    engine.add("name")
    engine.clear()
    assert engine.bookmarked == []


def test_unbookmarked_excludes_bookmarked(engine):
    engine.add("name")
    assert "name" not in engine.unbookmarked
    assert "id" in engine.unbookmarked
