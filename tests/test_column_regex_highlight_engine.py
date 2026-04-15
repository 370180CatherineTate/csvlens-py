"""Tests for ColumnRegexHighlightEngine."""
import pytest
from csvlens.column_regex_highlight_engine import ColumnRegexHighlightEngine


@pytest.fixture
def engine() -> ColumnRegexHighlightEngine:
    return ColumnRegexHighlightEngine(["name", "email", "notes"])


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnRegexHighlightEngine([])


def test_headers_property(engine):
    assert engine.headers == ["name", "email", "notes"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


def test_initial_no_rules(engine):
    assert engine.rules == {}


def test_set_rule_unknown_column_raises(engine):
    with pytest.raises(KeyError, match="Unknown column"):
        engine.set_rule("nonexistent", r"\d+")


def test_set_rule_empty_pattern_raises(engine):
    with pytest.raises(ValueError, match="pattern must not be empty"):
        engine.set_rule("name", "")


def test_set_rule_adds_entry(engine):
    engine.set_rule("name", r"Alice")
    assert "name" in engine.rules
    assert engine.rules["name"] == "Alice"


def test_has_rule_true_after_set(engine):
    engine.set_rule("email", r"@example\.com")
    assert engine.has_rule("email") is True


def test_has_rule_false_for_unset(engine):
    assert engine.has_rule("notes") is False


def test_spans_no_rule_returns_empty(engine):
    assert engine.spans("name", "Alice") == []


def test_spans_single_match(engine):
    engine.set_rule("name", r"Ali")
    result = engine.spans("name", "Alice")
    assert result == [(0, 3)]


def test_spans_multiple_matches(engine):
    engine.set_rule("notes", r"\d+")
    result = engine.spans("notes", "abc 12 def 34")
    assert result == [(4, 6), (11, 13)]


def test_spans_case_insensitive_by_default(engine):
    engine.set_rule("name", r"alice")
    result = engine.spans("name", "ALICE")
    assert result == [(0, 5)]


def test_spans_case_sensitive_option(engine):
    engine.set_rule("name", r"alice", case_sensitive=True)
    assert engine.spans("name", "ALICE") == []
    assert engine.spans("name", "alice") == [(0, 5)]


def test_clear_rule_removes_entry(engine):
    engine.set_rule("name", r"test")
    engine.clear_rule("name")
    assert engine.has_rule("name") is False
    assert engine.spans("name", "test") == []


def test_clear_rule_noop_when_absent(engine):
    engine.clear_rule("name")  # should not raise


def test_clear_all_removes_all_rules(engine):
    engine.set_rule("name", r"a")
    engine.set_rule("email", r"b")
    engine.clear_all()
    assert engine.rules == {}
