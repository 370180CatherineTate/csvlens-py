"""Tests for ColumnAggregateEngine and AggregateResult."""
import pytest

from csvlens.column_aggregate_engine import AggregateResult, ColumnAggregateEngine


@pytest.fixture
def engine():
    return ColumnAggregateEngine(["age", "score", "name"])


@pytest.fixture
def rows():
    return [
        {"age": "25", "score": "88.5", "name": "Alice"},
        {"age": "30", "score": "72.0", "name": "Bob"},
        {"age": "22", "score": "95.0", "name": "Carol"},
        {"age": "",   "score": "60.0", "name": "Dave"},
    ]


def test_empty_headers_raises():
    with pytest.raises(ValueError):
        ColumnAggregateEngine([])


def test_headers_property(engine):
    assert engine.headers == ["age", "score", "name"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


def test_result_before_compute_raises(engine):
    with pytest.raises(RuntimeError):
        engine.result("age")


def test_result_unknown_column_raises(engine):
    engine.compute([])
    with pytest.raises(KeyError):
        engine.result("nonexistent")


def test_numeric_column(engine, rows):
    engine.compute(rows)
    r = engine.result("age")
    assert r.numeric_count == 3  # blank skipped
    assert r.total == pytest.approx(77.0)
    assert r.mean == pytest.approx(77 / 3)
    assert r.minimum == pytest.approx(22.0)
    assert r.maximum == pytest.approx(30.0)


def test_all_non_numeric_column(engine, rows):
    engine.compute(rows)
    r = engine.result("name")
    assert r.numeric_count == 0
    assert r.total is None
    assert r.mean is None
    assert r.minimum is None
    assert r.maximum is None


def test_summary_keys(engine, rows):
    engine.compute(rows)
    keys = set(engine.result("score").summary().keys())
    assert keys == {"sum", "mean", "min", "max", "count"}


def test_all_results_returns_all_headers(engine, rows):
    engine.compute(rows)
    assert set(engine.all_results().keys()) == {"age", "score", "name"}


def test_empty_rows_produces_none_aggregates(engine):
    engine.compute([])
    r = engine.result("score")
    assert r.numeric_count == 0
    assert r.total is None


def test_aggregate_result_summary_count(engine, rows):
    engine.compute(rows)
    r = engine.result("score")
    assert r.summary()["count"] == 4.0
