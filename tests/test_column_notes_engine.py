"""Tests for ColumnNotesEngine."""
import pytest
from csvlens.column_notes_engine import ColumnNotesEngine


@pytest.fixture()
def engine() -> ColumnNotesEngine:
    return ColumnNotesEngine(["name", "age", "city", "score"])


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_empty_headers_raises() -> None:
    with pytest.raises(ValueError):
        ColumnNotesEngine([])


def test_headers_property(engine: ColumnNotesEngine) -> None:
    assert engine.headers == ["name", "age", "city", "score"]


def test_headers_returns_copy(engine: ColumnNotesEngine) -> None:
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------

def test_initial_notes_empty(engine: ColumnNotesEngine) -> None:
    assert engine.notes == {}


def test_initial_annotated_columns_empty(engine: ColumnNotesEngine) -> None:
    assert engine.annotated_columns() == []


# ---------------------------------------------------------------------------
# set_note / get_note
# ---------------------------------------------------------------------------

def test_set_note_stores_text(engine: ColumnNotesEngine) -> None:
    engine.set_note("age", "years since birth")
    assert engine.get_note("age") == "years since birth"


def test_set_note_strips_whitespace(engine: ColumnNotesEngine) -> None:
    engine.set_note("name", "  full name  ")
    assert engine.get_note("name") == "full name"


def test_set_note_overwrites_existing(engine: ColumnNotesEngine) -> None:
    engine.set_note("city", "first note")
    engine.set_note("city", "second note")
    assert engine.get_note("city") == "second note"


def test_set_note_empty_string_removes(engine: ColumnNotesEngine) -> None:
    engine.set_note("score", "important")
    engine.set_note("score", "   ")
    assert engine.get_note("score") is None


def test_get_note_unknown_column_raises(engine: ColumnNotesEngine) -> None:
    with pytest.raises(KeyError):
        engine.get_note("unknown")


def test_set_note_unknown_column_raises(engine: ColumnNotesEngine) -> None:
    with pytest.raises(KeyError):
        engine.set_note("unknown", "hello")


def test_get_note_returns_none_when_not_set(engine: ColumnNotesEngine) -> None:
    assert engine.get_note("age") is None


# ---------------------------------------------------------------------------
# clear_note
# ---------------------------------------------------------------------------

def test_clear_note_removes_entry(engine: ColumnNotesEngine) -> None:
    engine.set_note("name", "primary key")
    engine.clear_note("name")
    assert engine.get_note("name") is None


def test_clear_note_noop_when_not_set(engine: ColumnNotesEngine) -> None:
    engine.clear_note("age")  # should not raise


def test_clear_note_unknown_column_raises(engine: ColumnNotesEngine) -> None:
    with pytest.raises(KeyError):
        engine.clear_note("ghost")


# ---------------------------------------------------------------------------
# clear_all
# ---------------------------------------------------------------------------

def test_clear_all_removes_all_notes(engine: ColumnNotesEngine) -> None:
    engine.set_note("name", "n1")
    engine.set_note("age", "n2")
    engine.clear_all()
    assert engine.notes == {}


# ---------------------------------------------------------------------------
# annotated_columns
# ---------------------------------------------------------------------------

def test_annotated_columns_order(engine: ColumnNotesEngine) -> None:
    engine.set_note("score", "metric")
    engine.set_note("name", "identifier")
    # order should follow original header order
    assert engine.annotated_columns() == ["name", "score"]


def test_notes_returns_copy(engine: ColumnNotesEngine) -> None:
    engine.set_note("age", "years")
    d = engine.notes
    d["age"] = "tampered"
    assert engine.get_note("age") == "years"
