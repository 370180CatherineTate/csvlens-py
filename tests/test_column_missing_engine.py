"""Tests for ColumnMissingEngine."""
import pytest
from csvlens.column_missing_engine import ColumnMissingEngine, MissingSummary


HEADERS = ["name", "age", "email"]

ROWS = [
    {"name": "Alice", "age": "30", "email": "alice@example.com"},
    {"name": "", "age": "25", "email": "NULL"},
    {"name": "Bob", "age": "N/A", "email": ""},
    {"name": "Carol", "age": "40", "email": "carol@example.com"},
    {"name": "None", "age": "", "email": "dave@example.com"},
]


@pytest.fixture
def engine() -> ColumnMissingEngine:
    return ColumnMissingEngine(HEADERS, ROWS)


# ---------------------------------------------------------------------------
# construction guards
# ---------------------------------------------------------------------------

def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnMissingEngine([], ROWS)


# ---------------------------------------------------------------------------
# property access
# ---------------------------------------------------------------------------

def test_headers_property(engine):
    assert engine.headers == HEADERS


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


def test_summaries_property(engine):
    s = engine.summaries
    assert set(s.keys()) == set(HEADERS)


def test_summaries_returns_copy(engine):
    s1 = engine.summaries
    s1["name"] = None  # type: ignore[assignment]
    assert engine.summaries["name"] is not None


# ---------------------------------------------------------------------------
# missing counts
# ---------------------------------------------------------------------------

def test_name_missing_count(engine):
    # "" and "None" are both null values
    assert engine.get("name").missing == 2


def test_age_missing_count(engine):
    # "N/A" and "" are null values
    assert engine.get("age").missing == 2


def test_email_missing_count(engine):
    # "NULL" and "" are null values
    assert engine.get("email").missing == 2


def test_present_count(engine):
    s = engine.get("name")
    assert s.present == s.total - s.missing


def test_total_equals_row_count(engine):
    for col in HEADERS:
        assert engine.get(col).total == len(ROWS)


# ---------------------------------------------------------------------------
# percentage helpers
# ---------------------------------------------------------------------------

def test_missing_pct_range(engine):
    for col in HEADERS:
        pct = engine.get(col).missing_pct
        assert 0.0 <= pct <= 100.0


def test_present_pct_complements_missing_pct(engine):
    for col in HEADERS:
        s = engine.get(col)
        assert abs(s.missing_pct + s.present_pct - 100.0) < 0.01


def test_zero_total_pct():
    eng = ColumnMissingEngine(["x"], [])
    assert eng.get("x").missing_pct == 0.0
    assert eng.get("x").present_pct == 0.0


# ---------------------------------------------------------------------------
# summary dict
# ---------------------------------------------------------------------------

def test_summary_keys(engine):
    keys = engine.get("name").summary().keys()
    assert {"column", "total", "missing", "present", "missing_pct", "present_pct"} <= set(keys)


# ---------------------------------------------------------------------------
# get() error
# ---------------------------------------------------------------------------

def test_get_unknown_column_raises(engine):
    with pytest.raises(KeyError, match="Unknown column"):
        engine.get("nonexistent")


# ---------------------------------------------------------------------------
# most_missing
# ---------------------------------------------------------------------------

def test_most_missing_returns_string(engine):
    result = engine.most_missing()
    assert isinstance(result, str)
    assert result in HEADERS


def test_most_missing_empty_rows():
    eng = ColumnMissingEngine(["a", "b"], [])
    # all zeros — any column is acceptable, just must not raise
    result = eng.most_missing()
    assert result in ("a", "b")


# ---------------------------------------------------------------------------
# custom null values
# ---------------------------------------------------------------------------

def test_custom_null_values():
    rows = [{"score": "n/a"}, {"score": "99"}, {"score": "n/a"}]
    eng = ColumnMissingEngine(["score"], rows, null_values=["n/a"])
    assert eng.get("score").missing == 2


def test_default_null_values_exclude_non_null():
    rows = [{"val": "hello"}, {"val": "world"}]
    eng = ColumnMissingEngine(["val"], rows)
    assert eng.get("val").missing == 0
