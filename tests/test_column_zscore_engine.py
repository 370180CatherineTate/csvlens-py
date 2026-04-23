import math
import pytest
from csvlens.column_zscore_engine import _to_float, ColumnZScoreEngine, ZScoreResult


# ---------------------------------------------------------------------------
# _to_float helper
# ---------------------------------------------------------------------------

def test_to_float_valid():
    assert _to_float("3.14") == pytest.approx(3.14)
    assert _to_float("-1") == pytest.approx(-1.0)
    assert _to_float("0") == pytest.approx(0.0)


def test_to_float_invalid():
    assert _to_float("") is None
    assert _to_float("N/A") is None
    assert _to_float("abc") is None
    assert _to_float(None) is None  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

ROWS = [
    {"val": "10", "label": "a"},
    {"val": "20", "label": "b"},
    {"val": "30", "label": "c"},
    {"val": "40", "label": "d"},
    {"val": "50", "label": "e"},
]


@pytest.fixture
def engine():
    return ColumnZScoreEngine(["val", "label"], ROWS)


# ---------------------------------------------------------------------------
# Construction guards
# ---------------------------------------------------------------------------

def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnZScoreEngine([], ROWS)


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------

def test_headers_property(engine):
    assert engine.headers == ["val", "label"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert engine.headers == ["val", "label"]


def test_results_keys(engine):
    assert set(engine.results.keys()) == {"val", "label"}


# ---------------------------------------------------------------------------
# Z-score correctness
# ---------------------------------------------------------------------------

def test_numeric_column_scores_count(engine):
    result = engine.get("val")
    assert len(result.scores) == len(ROWS)


def test_numeric_column_mean_zero(engine):
    """Mean of z-scores should be ~0."""
    scores = [s for s in engine.get("val").scores if s is not None]
    assert sum(scores) == pytest.approx(0.0, abs=1e-9)


def test_numeric_column_std_one(engine):
    """Population std of z-scores should be ~1."""
    scores = [s for s in engine.get("val").scores if s is not None]
    mean = sum(scores) / len(scores)
    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    assert math.sqrt(variance) == pytest.approx(1.0, abs=1e-9)


def test_string_column_all_none(engine):
    """Non-numeric column produces all-None scores."""
    scores = engine.get("label").scores
    assert all(s is None for s in scores)


def test_outlier_count_no_outliers(engine):
    assert engine.get("val").outlier_count == 0


def test_outlier_count_with_outlier():
    rows = [
        {"x": str(i)} for i in range(20)
    ] + [{"x": "1000"}]
    eng = ColumnZScoreEngine(["x"], rows)
    assert eng.get("x").outlier_count >= 1


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def test_summary_contains_column_name(engine):
    assert "val" in engine.get("val").summary()


def test_summary_no_numeric_data():
    rows = [{"col": "foo"}, {"col": "bar"}]
    eng = ColumnZScoreEngine(["col"], rows)
    assert "no numeric data" in eng.get("col").summary()


# ---------------------------------------------------------------------------
# get() unknown column
# ---------------------------------------------------------------------------

def test_get_unknown_column_raises(engine):
    with pytest.raises(KeyError, match="Unknown column"):
        engine.get("nonexistent")


# ---------------------------------------------------------------------------
# Single-row edge case (std == 0 guard)
# ---------------------------------------------------------------------------

def test_single_row_scores_are_none():
    rows = [{"x": "42"}]
    eng = ColumnZScoreEngine(["x"], rows)
    assert eng.get("x").scores == [None]
