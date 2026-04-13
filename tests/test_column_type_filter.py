"""Tests for ColumnTypeFilter."""

import pytest
from csvlens.column_type_filter import ColumnTypeFilter, _infer_type


# ---------------------------------------------------------------------------
# _infer_type unit tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    ("42", "integer"),
    ("-7", "integer"),
    ("3.14", "float"),
    ("-0.5", "float"),
    ("true", "boolean"),
    ("False", "boolean"),
    ("yes", "boolean"),
    ("no", "boolean"),
    ("2024-01-15", "date"),
    ("hello", "string"),
    ("", "string"),
    ("  ", "string"),
])
def test_infer_type(value, expected):
    assert _infer_type(value) == expected


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

HEADERS = ["name", "age", "score", "active", "joined"]

ROWS = [
    {"name": "Alice", "age": "30", "score": "9.5", "active": "true",  "joined": "2021-03-01"},
    {"name": "Bob",   "age": "25", "score": "7.0", "active": "false", "joined": "2022-07-14"},
    {"name": "Carol", "age": "abc", "score": "8.2", "active": "yes",  "joined": "not-a-date"},
]


@pytest.fixture
def f():
    return ColumnTypeFilter(HEADERS)


# ---------------------------------------------------------------------------
# Constructor / property tests
# ---------------------------------------------------------------------------

def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnTypeFilter([])


def test_headers_property(f):
    assert f.headers == HEADERS


def test_initial_no_rules(f):
    assert f.rules == {}


# ---------------------------------------------------------------------------
# set_rule / clear_rule
# ---------------------------------------------------------------------------

def test_set_rule_unknown_column_raises(f):
    with pytest.raises(KeyError):
        f.set_rule("nonexistent", "integer")


def test_set_rule_invalid_type_raises(f):
    with pytest.raises(ValueError, match="Invalid type"):
        f.set_rule("age", "blob")


def test_set_rule_stores_lowercase(f):
    f.set_rule("age", "INTEGER")
    assert f.rules["age"] == "integer"


def test_clear_rule_specific(f):
    f.set_rule("age", "integer")
    f.set_rule("name", "string")
    f.clear_rule("age")
    assert "age" not in f.rules
    assert "name" in f.rules


def test_clear_rule_all(f):
    f.set_rule("age", "integer")
    f.set_rule("name", "string")
    f.clear_rule()
    assert f.rules == {}


# ---------------------------------------------------------------------------
# apply tests
# ---------------------------------------------------------------------------

def test_apply_no_rules_returns_all(f):
    assert f.apply(ROWS) == ROWS


def test_apply_integer_filter(f):
    f.set_rule("age", "integer")
    result = f.apply(ROWS)
    assert len(result) == 2
    assert all(r["age"].isdigit() or r["age"].lstrip("-").isdigit() for r in result)


def test_apply_boolean_filter(f):
    f.set_rule("active", "boolean")
    result = f.apply(ROWS)
    assert len(result) == 3  # all three qualify


def test_apply_date_filter(f):
    f.set_rule("joined", "date")
    result = f.apply(ROWS)
    assert len(result) == 2
    assert all(r["name"] in ("Alice", "Bob") for r in result)


def test_apply_multiple_rules(f):
    f.set_rule("age", "integer")
    f.set_rule("joined", "date")
    result = f.apply(ROWS)
    assert len(result) == 2


def test_apply_empty_rows(f):
    f.set_rule("age", "integer")
    assert f.apply([]) == []


def test_rules_returns_copy(f):
    f.set_rule("age", "integer")
    copy = f.rules
    copy["name"] = "string"
    assert "name" not in f.rules
