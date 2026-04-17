import pytest
from csvlens.column_lock_engine import ColumnLockEngine


@pytest.fixture
def engine():
    return ColumnLockEngine(["id", "name", "age", "email"])


def test_empty_headers_raises():
    with pytest.raises(ValueError):
        ColumnLockEngine([])


def test_headers_property(engine):
    assert engine.headers == ["id", "name", "age", "email"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


def test_initial_none_locked(engine):
    assert engine.locked == []


def test_initial_all_unlocked(engine):
    assert engine.unlocked == ["id", "name", "age", "email"]


def test_lock_column(engine):
    engine.lock("name")
    assert "name" in engine.locked
    assert "name" not in engine.unlocked


def test_lock_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.lock("nonexistent")


def test_unlock_column(engine):
    engine.lock("age")
    engine.unlock("age")
    assert "age" not in engine.locked
    assert "age" in engine.unlocked


def test_unlock_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.unlock("nonexistent")


def test_unlock_already_unlocked_is_safe(engine):
    engine.unlock("id")  # should not raise
    assert "id" not in engine.locked


def test_is_locked_true(engine):
    engine.lock("email")
    assert engine.is_locked("email") is True


def test_is_locked_false(engine):
    assert engine.is_locked("id") is False


def test_is_locked_unknown_raises(engine):
    with pytest.raises(KeyError):
        engine.is_locked("ghost")


def test_lock_all(engine):
    engine.lock_all()
    assert engine.locked == ["id", "name", "age", "email"]
    assert engine.unlocked == []


def test_unlock_all(engine):
    engine.lock_all()
    engine.unlock_all()
    assert engine.locked == []
    assert engine.unlocked == ["id", "name", "age", "email"]


def test_toggle_locks_unlocked(engine):
    result = engine.toggle("name")
    assert result is True
    assert engine.is_locked("name") is True


def test_toggle_unlocks_locked(engine):
    engine.lock("name")
    result = engine.toggle("name")
    assert result is False
    assert engine.is_locked("name") is False


def test_toggle_unknown_raises(engine):
    with pytest.raises(KeyError):
        engine.toggle("ghost")


def test_locked_preserves_header_order(engine):
    engine.lock("email")
    engine.lock("id")
    assert engine.locked == ["id", "email"]
