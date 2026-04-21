"""Tests for ColumnNullEngine and NullSummary."""
import pytest

from csvlens.column_null_engine import ColumnNullEngine, NullSummary


HEADERS = ["name", "age", "city"]

ROWS = [
    {"name": "Alice", "age": "30", "city": "London"},
    {"name": "Bob",   "age": "",   "city": "Paris"},
    {"name": "",      "age": "25", "city": ""},
    {"name": "Dana",  "age": "",   "city": "Berlin"},
    {"name": "Eve",   "age": "22", "city": "London"},
]


@pytest.fixture
def engine() -> ColumnNullEngine:
    return ColumnNullEngine(HEADERS, ROWS)


# ---------------------------------------------------------------------------
# Construction guards
# ---------------------------------------------------------------------------

def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnNullEngine([], ROWS)


# ---------------------------------------------------------------------------
# Properties
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
    s = engine.summaries
    s["name"] = None  # type: ignore[assignment]
    assert engine.summaries["name"] is not None


# ---------------------------------------------------------------------------
# NullSummary values
# ---------------------------------------------------------------------------

def test_name_null_count(engine):
    s = engine.summary("name")
    assert s.null_count == 1  # row index 2


def test_age_null_count(engine):
    s = engine.summary("age")
    assert s.null_count == 2  # rows 1 and 3


def test_city_null_count(engine):
    s = engine.summary("city")
    assert s.null_count == 1  # row index 2


def test_null_rate_age(engine):
    s = engine.summary("age")
    assert s.null_rate == pytest.approx(2 / 5)


def test_non_null_count(engine):
    s = engine.summary("name")
    assert s.non_null_count == 4


def test_null_rate_zero_rows():
    eng = ColumnNullEngine(["x"], [])
    assert eng.summary("x").null_rate == 0.0


def test_summary_unknown_column_raises(engine):
    with pytest.raises(KeyError, match="unknown"):
        engine.summary("unknown")


# ---------------------------------------------------------------------------
# Row filtering
# ---------------------------------------------------------------------------

def test_filter_rows_with_nulls(engine):
    rows = engine.filter_rows_with_nulls("age")
    assert len(rows) == 2
    assert all(r["age"] == "" for r in rows)


def test_filter_rows_without_nulls(engine):
    rows = engine.filter_rows_without_nulls("age")
    assert len(rows) == 3
    assert all(r["age"] != "" for r in rows)


def test_filter_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.filter_rows_with_nulls("unknown")


# ---------------------------------------------------------------------------
# columns_above_null_rate
# ---------------------------------------------------------------------------

def test_columns_above_null_rate(engine):
    # age has 40 % nulls, others have 20 %
    cols = engine.columns_above_null_rate(0.30)
    assert "age" in cols
    assert "name" not in cols


def test_columns_above_null_rate_zero_threshold(engine):
    # All columns have at least one null
    cols = engine.columns_above_null_rate(0.0)
    assert set(cols) == {"name", "age", "city"}


def test_columns_above_null_rate_one_threshold(engine):
    cols = engine.columns_above_null_rate(1.0)
    assert cols == []


def test_columns_above_null_rate_invalid_threshold(engine):
    with pytest.raises(ValueError, match="threshold"):
        engine.columns_above_null_rate(1.5)
