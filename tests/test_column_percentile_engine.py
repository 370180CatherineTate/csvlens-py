"""Tests for ColumnPercentileEngine."""

import pytest

from csvlens.column_percentile_engine import (
    ColumnPercentileEngine,
    PercentileResult,
    _to_float,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

ROWS = [
    {"age": "10", "score": "1.0", "label": "a"},
    {"age": "20", "score": "2.0", "label": "b"},
    {"age": "30", "score": "3.0", "label": "c"},
    {"age": "40", "score": "4.0", "label": "d"},
    {"age": "50", "score": "5.0", "label": "e"},
]

HEADERS = ["age", "score", "label"]


@pytest.fixture
def engine() -> ColumnPercentileEngine:
    return ColumnPercentileEngine(HEADERS, ROWS)


# ---------------------------------------------------------------------------
# _to_float
# ---------------------------------------------------------------------------


def test_to_float_valid():
    assert _to_float("3.14") == pytest.approx(3.14)


def test_to_float_invalid():
    assert _to_float("n/a") is None
    assert _to_float("") is None


# ---------------------------------------------------------------------------
# construction guards
# ---------------------------------------------------------------------------


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnPercentileEngine([], ROWS)


def test_invalid_percentile_raises():
    with pytest.raises(ValueError, match="between 0 and 100"):
        ColumnPercentileEngine(HEADERS, ROWS, percentiles=[10, 110])


# ---------------------------------------------------------------------------
# properties
# ---------------------------------------------------------------------------


def test_headers_property(engine):
    assert engine.headers == HEADERS


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert engine.headers == HEADERS


def test_percentiles_property(engine):
    assert set(engine.percentiles) == {10, 25, 50, 75, 90}


def test_results_keys(engine):
    assert set(engine.results.keys()) == set(HEADERS)


# ---------------------------------------------------------------------------
# PercentileResult correctness
# ---------------------------------------------------------------------------


def test_median_numeric_column(engine):
    result = engine.get("age")
    assert isinstance(result, PercentileResult)
    assert result.get(50) == pytest.approx(30.0)


def test_p25_p75(engine):
    result = engine.get("age")
    assert result.get(25) == pytest.approx(20.0)
    assert result.get(75) == pytest.approx(40.0)


def test_non_numeric_column_count_zero(engine):
    result = engine.get("label")
    assert result.count == 0
    assert result.get(50) is None


def test_summary_contains_column(engine):
    s = engine.get("score").summary()
    assert s["column"] == "score"
    assert "p50" in s
    assert "count" in s


def test_get_unknown_column_raises(engine):
    with pytest.raises(KeyError, match="unknown column"):
        engine.get("nonexistent")


def test_custom_percentiles():
    eng = ColumnPercentileEngine(HEADERS, ROWS, percentiles=[0, 100])
    result = eng.get("age")
    assert result.get(0) == pytest.approx(10.0)
    assert result.get(100) == pytest.approx(50.0)


def test_empty_rows_returns_none_percentiles():
    eng = ColumnPercentileEngine(HEADERS, [])
    result = eng.get("age")
    assert result.count == 0
    assert result.get(50) is None
