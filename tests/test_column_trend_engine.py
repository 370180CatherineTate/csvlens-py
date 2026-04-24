"""Tests for ColumnTrendEngine and ColumnTrendRenderer."""
import pytest

from csvlens.column_trend_engine import ColumnTrendEngine, TrendResult, _to_float
from csvlens.column_trend_renderer import ColumnTrendRenderer


# ---------------------------------------------------------------------------
# helpers / fixtures
# ---------------------------------------------------------------------------

ROWS_RISING = [
    {"val": "1", "label": "a"},
    {"val": "2", "label": "b"},
    {"val": "3", "label": "c"},
    {"val": "4", "label": "d"},
]

ROWS_FALLING = [
    {"val": "10", "label": "x"},
    {"val": "7",  "label": "y"},
    {"val": "4",  "label": "z"},
]

ROWS_FLAT = [
    {"val": "5", "label": "p"},
    {"val": "5", "label": "q"},
    {"val": "5", "label": "r"},
]

ROWS_MIXED_NULLS = [
    {"val": "abc", "label": "p"},
    {"val": "2",   "label": "q"},
    {"val": "",    "label": "r"},
    {"val": "6",   "label": "s"},
]


@pytest.fixture
def engine():
    return ColumnTrendEngine(["val", "label"])


@pytest.fixture
def renderer(engine):
    engine.compute(ROWS_RISING)
    return ColumnTrendRenderer(engine, col_width=14)


# ---------------------------------------------------------------------------
# _to_float
# ---------------------------------------------------------------------------

def test_to_float_valid():
    assert _to_float("3.14") == pytest.approx(3.14)


def test_to_float_invalid():
    assert _to_float("abc") is None
    assert _to_float("") is None
    assert _to_float(None) is None  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# ColumnTrendEngine
# ---------------------------------------------------------------------------

def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnTrendEngine([])


def test_headers_property(engine):
    assert engine.headers == ["val", "label"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert engine.headers == ["val", "label"]


def test_rising_trend(engine):
    engine.compute(ROWS_RISING)
    r = engine.get("val")
    assert r.direction == "up"
    assert r.slope > 0
    assert r.count == 4


def test_falling_trend():
    e = ColumnTrendEngine(["val", "label"])
    e.compute(ROWS_FALLING)
    r = e.get("val")
    assert r.direction == "down"
    assert r.slope < 0


def test_flat_trend():
    e = ColumnTrendEngine(["val", "label"])
    e.compute(ROWS_FLAT)
    r = e.get("val")
    assert r.direction == "flat"
    assert r.slope == pytest.approx(0.0)


def test_non_numeric_column(engine):
    engine.compute(ROWS_RISING)
    r = engine.get("label")
    assert r.direction == "flat"
    assert r.count == 0


def test_mixed_nulls_uses_only_numeric():
    e = ColumnTrendEngine(["val", "label"])
    e.compute(ROWS_MIXED_NULLS)
    r = e.get("val")
    assert r.count == 2  # only "2" and "6" are numeric


def test_single_row_is_flat():
    e = ColumnTrendEngine(["val"])
    e.compute([{"val": "42"}])
    r = e.get("val")
    assert r.direction == "flat"
    assert r.slope == pytest.approx(0.0)


def test_get_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.get("nonexistent")


def test_get_before_compute_returns_flat(engine):
    r = engine.get("val")
    assert r.direction == "flat"
    assert r.count == 0


def test_results_property(engine):
    engine.compute(ROWS_RISING)
    results = engine.results
    assert set(results.keys()) == {"val", "label"}


def test_trend_result_summary():
    r = TrendResult(column="x", count=5, slope=0.5, direction="up")
    s = r.summary
    assert "↑" in s
    assert "slope" in s
    assert "n=5" in s


# ---------------------------------------------------------------------------
# ColumnTrendRenderer
# ---------------------------------------------------------------------------

def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError, match="col_width"):
        ColumnTrendRenderer(engine, col_width=3)


def test_col_width_property(renderer):
    assert renderer.col_width == 14


def test_render_returns_string(renderer):
    result = renderer.render(["val", "label"])
    assert isinstance(result, str)


def test_render_header_returns_string(renderer):
    result = renderer.render_header(["val", "label"])
    assert isinstance(result, str)
    assert "val" in result


def test_render_contains_arrow(renderer):
    result = renderer.render(["val"])
    assert any(arrow in result for arrow in ("↑", "↓", "→"))
