import math
import pytest

from csvlens.column_correlation_engine import (
    ColumnCorrelationEngine,
    CorrelationResult,
    _to_float,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

ROWS = [
    {"x": "1", "y": "2",  "z": "hello"},
    {"x": "2", "y": "4",  "z": "world"},
    {"x": "3", "y": "6",  "z": "foo"},
    {"x": "4", "y": "8",  "z": "bar"},
    {"x": "5", "y": "10", "z": "baz"},
]

HEADERS = ["x", "y", "z"]


@pytest.fixture
def engine():
    return ColumnCorrelationEngine(HEADERS, ROWS)


# ---------------------------------------------------------------------------
# _to_float
# ---------------------------------------------------------------------------

def test_to_float_valid():
    assert _to_float("3.14") == pytest.approx(3.14)


def test_to_float_invalid():
    assert _to_float("abc") is None


def test_to_float_none():
    assert _to_float(None) is None


# ---------------------------------------------------------------------------
# construction
# ---------------------------------------------------------------------------

def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers"):
        ColumnCorrelationEngine([], ROWS)


def test_headers_property(engine):
    assert engine.headers == HEADERS


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


# ---------------------------------------------------------------------------
# compute – basic
# ---------------------------------------------------------------------------

def test_perfect_positive_correlation(engine):
    result = engine.compute("x", "y")
    assert result.r == pytest.approx(1.0, abs=1e-9)


def test_correlation_n(engine):
    result = engine.compute("x", "y")
    assert result.n == 5


def test_unknown_col_a_raises(engine):
    with pytest.raises(KeyError):
        engine.compute("missing", "y")


def test_unknown_col_b_raises(engine):
    with pytest.raises(KeyError):
        engine.compute("x", "missing")


# ---------------------------------------------------------------------------
# non-numeric / insufficient data
# ---------------------------------------------------------------------------

def test_non_numeric_column_returns_none(engine):
    result = engine.compute("x", "z")
    assert result.r is None


def test_single_row_returns_none():
    eng = ColumnCorrelationEngine(["a", "b"], [{"a": "1", "b": "2"}])
    result = eng.compute("a", "b")
    assert result.r is None
    assert result.n == 1


# ---------------------------------------------------------------------------
# strength labels
# ---------------------------------------------------------------------------

def test_strength_very_strong(engine):
    result = engine.compute("x", "y")
    assert result.strength == "very strong"


def test_strength_na_when_r_none(engine):
    result = engine.compute("x", "z")
    assert result.strength == "n/a"


# ---------------------------------------------------------------------------
# caching
# ---------------------------------------------------------------------------

def test_result_is_cached(engine):
    r1 = engine.compute("x", "y")
    r2 = engine.compute("x", "y")
    assert r1 is r2
