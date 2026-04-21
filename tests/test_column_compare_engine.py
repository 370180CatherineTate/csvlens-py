"""Tests for ColumnCompareEngine and CompareResult."""
import pytest
from csvlens.column_compare_engine import (
    ColumnCompareEngine,
    CompareResult,
    _to_float,
)


@pytest.fixture
def engine():
    return ColumnCompareEngine(["a", "b", "c", "d"])


def test_to_float_valid():
    assert _to_float("3.14") == pytest.approx(3.14)
    assert _to_float("-7") == -7.0


def test_to_float_invalid():
    assert _to_float("hello") is None
    assert _to_float("") is None


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnCompareEngine([])


def test_headers_property(engine):
    assert engine.headers == ["a", "b", "c", "d"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("x")
    assert "x" not in engine.headers


def test_initial_no_rules(engine):
    assert engine.rules == {}


def test_set_rule_diff(engine):
    engine.set_rule("a", "b", "diff")
    assert ("a", "b") in engine.rules
    assert engine.rules[("a", "b")] == "diff"


def test_set_rule_invalid_column_raises(engine):
    with pytest.raises(KeyError):
        engine.set_rule("a", "z", "diff")


def test_set_rule_invalid_mode_raises(engine):
    with pytest.raises(ValueError, match="mode must be one of"):
        engine.set_rule("a", "b", "bad")


def test_clear_rule(engine):
    engine.set_rule("a", "b")
    engine.clear_rule("a", "b")
    assert ("a", "b") not in engine.rules


def test_clear_nonexistent_rule_noop(engine):
    engine.clear_rule("a", "b")  # should not raise


def test_compare_row_diff(engine):
    engine.set_rule("a", "b", "diff")
    row = {"a": "10", "b": "3", "c": "", "d": ""}
    results = engine.compare_row(row)
    r = results[("a", "b")]
    assert r.diff == pytest.approx(7.0)
    assert r.match is None
    assert r.label() == "+7"


def test_compare_row_eq_true(engine):
    engine.set_rule("a", "b", "eq")
    row = {"a": "5", "b": "5", "c": "", "d": ""}
    r = engine.compare_row(row)[("a", "b")]
    assert r.match is True
    assert r.label() == "✓"


def test_compare_row_eq_false(engine):
    engine.set_rule("a", "b", "eq")
    row = {"a": "5", "b": "6", "c": "", "d": ""}
    r = engine.compare_row(row)[("a", "b")]
    assert r.match is False
    assert r.label() == "✗"


def test_compare_row_string_eq(engine):
    engine.set_rule("a", "b", "eq")
    row = {"a": "hello", "b": "hello", "c": "", "d": ""}
    r = engine.compare_row(row)[("a", "b")]
    assert r.match is True


def test_compare_row_diff_non_numeric(engine):
    engine.set_rule("a", "b", "diff")
    row = {"a": "foo", "b": "bar", "c": "", "d": ""}
    r = engine.compare_row(row)[("a", "b")]
    assert r.diff is None
    assert r.label() == "N/A"


def test_rules_returns_copy(engine):
    engine.set_rule("a", "b")
    rules = engine.rules
    rules[("x", "y")] = "diff"
    assert ("x", "y") not in engine.rules
