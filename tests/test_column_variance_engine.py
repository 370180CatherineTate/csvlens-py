import pytest
from csvlens.column_variance_engine import ColumnVarianceEngine, _to_float


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def rows():
    return [
        {"a": "1", "b": "foo", "c": "10"},
        {"a": "2", "b": "bar", "c": "20"},
        {"a": "3", "b": "",    "c": "30"},
        {"a": "4", "b": "baz", "c": "40"},
        {"a": "5", "b": "qux", "c": "50"},
    ]


@pytest.fixture
def engine(rows):
    return ColumnVarianceEngine(["a", "b", "c"], rows)


# ---------------------------------------------------------------------------
# _to_float
# ---------------------------------------------------------------------------

def test_to_float_valid():
    assert _to_float("3.14") == pytest.approx(3.14)


def test_to_float_invalid():
    assert _to_float("abc") is None
    assert _to_float("") is None
    assert _to_float(None) is None


# ---------------------------------------------------------------------------
# construction guards
# ---------------------------------------------------------------------------

def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers"):
        ColumnVarianceEngine([], [])


# ---------------------------------------------------------------------------
# properties
# ---------------------------------------------------------------------------

def test_headers_property(engine):
    assert engine.headers == ["a", "b", "c"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("x")
    assert engine.headers == ["a", "b", "c"]


def test_results_keys(engine):
    assert set(engine.results.keys()) == {"a", "b", "c"}


# ---------------------------------------------------------------------------
# numeric column
# ---------------------------------------------------------------------------

def test_numeric_variance(engine):
    r = engine.get("a")
    assert r.variance is not None
    assert r.variance == pytest.approx(2.5)


def test_numeric_std_dev(engine):
    import math
    r = engine.get("a")
    assert r.std_dev == pytest.approx(math.sqrt(2.5))


def test_numeric_mean(engine):
    r = engine.get("a")
    assert r.mean == pytest.approx(3.0)


def test_numeric_cv(engine):
    r = engine.get("a")
    import math
    expected_cv = math.sqrt(2.5) / 3.0
    assert r.cv == pytest.approx(expected_cv)


def test_numeric_count(engine):
    r = engine.get("a")
    assert r.count == 5
    assert r.numeric_count == 5


# ---------------------------------------------------------------------------
# non-numeric column
# ---------------------------------------------------------------------------

def test_non_numeric_variance_is_none(engine):
    r = engine.get("b")
    assert r.variance is None
    assert r.std_dev is None
    assert r.cv is None


def test_non_numeric_numeric_count(engine):
    r = engine.get("b")
    assert r.numeric_count == 0


# ---------------------------------------------------------------------------
# summary string
# ---------------------------------------------------------------------------

def test_summary_numeric(engine):
    s = engine.get("a").summary()
    assert "var=" in s
    assert "std=" in s
    assert "mean=" in s


def test_summary_non_numeric(engine):
    s = engine.get("b").summary()
    assert "no numeric data" in s


# ---------------------------------------------------------------------------
# unknown column
# ---------------------------------------------------------------------------

def test_get_unknown_column_raises(engine):
    with pytest.raises(KeyError, match="unknown"):
        engine.get("unknown")


# ---------------------------------------------------------------------------
# single-row edge case
# ---------------------------------------------------------------------------

def test_single_row_variance_is_none():
    eng = ColumnVarianceEngine(["x"], [{"x": "42"}])
    r = eng.get("x")
    assert r.variance is None
    assert r.mean == pytest.approx(42.0)
