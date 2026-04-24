"""Tests for ColumnAnomalyEngine."""
import pytest
from csvlens.column_anomaly_engine import _to_float, AnomalyResult, ColumnAnomalyEngine


HEADERS = ["value", "label"]

ROWS = [
    {"value": str(v), "label": "x"}
    for v in [10, 12, 11, 13, 10, 12, 11, 100, 9, 11]
]


@pytest.fixture
def engine():
    return ColumnAnomalyEngine(HEADERS, ROWS)


def test_to_float_valid():
    assert _to_float("3.14") == pytest.approx(3.14)


def test_to_float_invalid():
    assert _to_float("abc") is None
    assert _to_float("") is None
    assert _to_float(None) is None


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnAnomalyEngine([], ROWS)


def test_non_positive_multiplier_raises():
    with pytest.raises(ValueError, match="multiplier must be positive"):
        ColumnAnomalyEngine(HEADERS, ROWS, multiplier=0)


def test_headers_property(engine):
    assert engine.headers == HEADERS


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert engine.headers == HEADERS


def test_multiplier_property(engine):
    assert engine.multiplier == 1.5


def test_results_keys(engine):
    assert set(engine.results.keys()) == set(HEADERS)


def test_numeric_column_detects_outlier(engine):
    result = engine.get("value")
    assert isinstance(result, AnomalyResult)
    assert result.anomaly_count >= 1
    assert result.iqr is not None


def test_anomaly_indices_valid(engine):
    result = engine.get("value")
    for idx in result.anomaly_indices:
        assert 0 <= idx < len(ROWS)


def test_non_numeric_column_no_anomalies(engine):
    result = engine.get("label")
    assert result.anomaly_count == 0
    assert result.iqr is None


def test_anomaly_pct_range(engine):
    result = engine.get("value")
    assert 0.0 <= result.anomaly_pct <= 100.0


def test_summary_contains_column(engine):
    result = engine.get("value")
    assert "value" in result.summary


def test_get_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.get("nonexistent")


def test_few_rows_no_anomalies():
    rows = [{"v": "1"}, {"v": "2"}]
    eng = ColumnAnomalyEngine(["v"], rows)
    result = eng.get("v")
    assert result.anomaly_count == 0
    assert result.iqr is None


def test_custom_multiplier():
    rows = [{"v": str(i)} for i in range(20)] + [{"v": "1000"}]
    eng = ColumnAnomalyEngine(["v"], rows, multiplier=3.0)
    result = eng.get("v")
    assert result.anomaly_count >= 1
