"""Tests for ColumnWrapEngine."""
import pytest
from csvlens.column_wrap_engine import ColumnWrapEngine


@pytest.fixture
def engine() -> ColumnWrapEngine:
    return ColumnWrapEngine(["name", "description", "notes"], wrap_width=10)


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="empty"):
        ColumnWrapEngine([])


def test_wrap_width_too_small_raises():
    with pytest.raises(ValueError, match="wrap_width"):
        ColumnWrapEngine(["a"], wrap_width=3)


def test_headers_property(engine):
    assert engine.headers == ["name", "description", "notes"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


def test_wrap_width_property(engine):
    assert engine.wrap_width == 10


def test_initial_no_wrapped_columns(engine):
    assert engine.wrapped_columns == []


def test_is_wrapped_default_false(engine):
    assert engine.is_wrapped("name") is False


def test_is_wrapped_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.is_wrapped("nonexistent")


def test_enable_sets_wrapped(engine):
    engine.enable("description")
    assert engine.is_wrapped("description") is True


def test_enable_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.enable("ghost")


def test_disable_clears_wrapped(engine):
    engine.enable("notes")
    engine.disable("notes")
    assert engine.is_wrapped("notes") is False


def test_disable_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.disable("ghost")


def test_toggle_enables_then_disables(engine):
    result1 = engine.toggle("name")
    assert result1 is True
    result2 = engine.toggle("name")
    assert result2 is False


def test_wrapped_columns_lists_enabled(engine):
    engine.enable("name")
    engine.enable("notes")
    assert set(engine.wrapped_columns) == {"name", "notes"}


def test_wrap_cell_no_wrap_returns_single_line(engine):
    lines = engine.wrap_cell("name", "hello world")
    assert lines == ["hello world"]


def test_wrap_cell_short_text_single_line(engine):
    engine.enable("description")
    lines = engine.wrap_cell("description", "short")
    assert lines == ["short"]


def test_wrap_cell_wraps_on_spaces(engine):
    engine.enable("description")
    # wrap_width=10; "hello" + " " + "world" = 11 chars -> wraps
    lines = engine.wrap_cell("description", "hello world")
    assert lines == ["hello", "world"]


def test_wrap_cell_hard_wraps_long_word(engine):
    engine.enable("description")
    long_word = "a" * 25  # 25 chars, wrap_width=10
    lines = engine.wrap_cell("description", long_word)
    assert all(len(l) <= 10 for l in lines)
    assert "".join(lines) == long_word


def test_wrap_cell_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.wrap_cell("ghost", "text")


def test_wrap_cell_multiword_sentence(engine):
    engine.enable("notes")
    text = "one two three four five"
    lines = engine.wrap_cell("notes", text)
    # Every line must be <= wrap_width
    assert all(len(l) <= 10 for l in lines)
    # Reconstructed text must equal original
    assert " ".join(lines) == text
