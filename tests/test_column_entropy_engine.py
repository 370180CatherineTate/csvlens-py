"""Tests for ColumnEntropyEngine."""
import math
import pytest
from csvlens.column_entropy_engine import ColumnEntropyEngine, EntropyResult

HEADERS = ["name", "score", "flag"]

ROWS = [
    {"name": "alice", "score": "10", "flag": "yes"},
    {"name": "bob",   "score": "20", "flag": "no"},
    {"name": "carol", "score": "10", "flag": "yes"},
    {"name": "dave",  "score": "30", "flag": "yes"},
]


@pytest.fixture
def engine():
    return ColumnEntropyEngine(HEADERS, ROWS)


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnEntropyEngine([], ROWS)


def test_headers_property(engine):
    assert engine.headers == HEADERS


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert engine.headers == HEADERS


def test_results_keys(engine):
    assert set(engine.results.keys()) == set(HEADERS)


def test_get_known_column(engine):
    result = engine.get("name")
    assert isinstance(result, EntropyResult)
    assert result.column == "name"


def test_get_unknown_column_raises(engine):
    with pytest.raises(KeyError, match="Unknown column"):
        engine.get("nonexistent")


def test_uniform_distribution_max_entropy():
    """Four distinct values → entropy == log2(4) == 2.0."""
    rows = [{"x": v} for v in ["a", "b", "c", "d"]]
    eng = ColumnEntropyEngine(["x"], rows)
    result = eng.get("x")
    assert result.entropy == pytest.approx(2.0, abs=1e-5)
    assert result.unique == 4
    assert result.total == 4


def test_constant_column_zero_entropy():
    """All identical values → entropy == 0."""
    rows = [{"x": "same"} for _ in range(5)]
    eng = ColumnEntropyEngine(["x"], rows)
    result = eng.get("x")
    assert result.entropy == pytest.approx(0.0, abs=1e-9)


def test_empty_rows_returns_none_entropy():
    eng = ColumnEntropyEngine(["x"], [])
    result = eng.get("x")
    assert result.entropy is None
    assert result.total == 0


def test_normalised_uniform():
    rows = [{"x": v} for v in ["a", "b", "c", "d"]]
    eng = ColumnEntropyEngine(["x"], rows)
    assert eng.get("x").normalised == pytest.approx(1.0, abs=1e-5)


def test_normalised_none_when_unique_less_than_two():
    rows = [{"x": "only"}]
    eng = ColumnEntropyEngine(["x"], rows)
    assert eng.get("x").normalised is None


def test_ranked_descending(engine):
    ranked = engine.ranked(descending=True)
    entropies = [r.entropy for r in ranked]
    assert entropies == sorted(entropies, reverse=True)


def test_ranked_ascending(engine):
    ranked = engine.ranked(descending=False)
    entropies = [r.entropy for r in ranked]
    assert entropies == sorted(entropies)


def test_flag_column_entropy(engine):
    """flag has 3 'yes' and 1 'no' → entropy = -(0.75*log2(0.75) + 0.25*log2(0.25))."""
    expected = -(0.75 * math.log2(0.75) + 0.25 * math.log2(0.25))
    result = engine.get("flag")
    assert result.entropy == pytest.approx(expected, abs=1e-5)
    assert result.unique == 2
    assert result.total == 4
