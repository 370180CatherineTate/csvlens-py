"""Tests for ColumnHeatmapEngine."""
import pytest
from csvlens.column_heatmap_engine import ColumnHeatmapEngine, _to_float


ROWS = [
    {"score": "10", "label": "alpha"},
    {"score": "50", "label": "beta"},
    {"score": "90", "label": "gamma"},
    {"score": "",   "label": "delta"},
]


@pytest.fixture
def engine():
    return ColumnHeatmapEngine(["score", "label"], ROWS)


def test_to_float_valid():
    assert _to_float("3.14") == pytest.approx(3.14)


def test_to_float_invalid():
    assert _to_float("abc") is None
    assert _to_float("") is None


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnHeatmapEngine([], ROWS)


def test_headers_property(engine):
    assert engine.headers == ["score", "label"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


def test_initial_no_heatmap_columns(engine):
    assert engine.heatmap_columns == []


def test_enable_column(engine):
    engine.enable("score")
    assert "score" in engine.heatmap_columns


def test_enable_unknown_column_raises(engine):
    with pytest.raises(KeyError, match="unknown_col"):
        engine.enable("unknown_col")


def test_disable_column(engine):
    engine.enable("score")
    engine.disable("score")
    assert "score" not in engine.heatmap_columns


def test_heat_returns_none_when_disabled(engine):
    assert engine.heat("score", "50") is None


def test_heat_min_value(engine):
    engine.enable("score")
    assert engine.heat("score", "10") == pytest.approx(0.0)


def test_heat_max_value(engine):
    engine.enable("score")
    assert engine.heat("score", "90") == pytest.approx(1.0)


def test_heat_mid_value(engine):
    engine.enable("score")
    result = engine.heat("score", "50")
    assert result == pytest.approx(0.5, abs=0.01)


def test_heat_non_numeric_returns_none(engine):
    engine.enable("score")
    assert engine.heat("score", "") is None


def test_heat_non_numeric_column_returns_none(engine):
    engine.enable("label")
    # label has no numeric range so not in heatmap_columns
    assert engine.heat("label", "alpha") is None


def test_heat_clamped_below_zero(engine):
    engine.enable("score")
    result = engine.heat("score", "-999")
    assert result == pytest.approx(0.0)


def test_heat_clamped_above_one(engine):
    engine.enable("score")
    result = engine.heat("score", "9999")
    assert result == pytest.approx(1.0)
