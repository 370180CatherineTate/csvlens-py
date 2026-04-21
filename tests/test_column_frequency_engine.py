import pytest

from csvlens.column_frequency_engine import ColumnFrequencyEngine, FrequencyResult


ROWS = [
    {"city": "London", "country": "UK", "score": "1"},
    {"city": "Paris", "country": "FR", "score": "2"},
    {"city": "London", "country": "UK", "score": "3"},
    {"city": "Berlin", "country": "DE", "score": ""},
    {"city": "London", "country": "UK", "score": "1"},
]
HEADERS = ["city", "country", "score"]


@pytest.fixture
def engine():
    return ColumnFrequencyEngine(HEADERS, ROWS)


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnFrequencyEngine([], ROWS)


def test_headers_property(engine):
    assert engine.headers == HEADERS


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert engine.headers == HEADERS


def test_unknown_column_raises(engine):
    with pytest.raises(KeyError, match="Unknown column"):
        engine.compute("nonexistent")


def test_compute_returns_frequency_result(engine):
    result = engine.compute("city")
    assert isinstance(result, FrequencyResult)


def test_total_matches_row_count(engine):
    result = engine.compute("city")
    assert result.total == len(ROWS)


def test_top_values_sorted_by_count(engine):
    top = engine.compute("city").top(3)
    assert top[0][0] == "London"
    assert top[0][1] == 3


def test_top_pct_sums_roughly_100(engine):
    top = engine.compute("city").top(10)
    total_pct = sum(t[2] for t in top)
    assert abs(total_pct - 100.0) < 0.5


def test_unique_count(engine):
    assert engine.compute("city").unique_count() == 3
    assert engine.compute("country").unique_count() == 3


def test_empty_string_counted(engine):
    result = engine.compute("score")
    values = {v for v, _, _ in result.top(10)}
    assert "" in values


def test_top_n_too_small_raises(engine):
    result = engine.compute("city")
    with pytest.raises(ValueError, match="n must be at least 1"):
        result.top(0)


def test_cache_is_reused(engine):
    r1 = engine.compute("city")
    r2 = engine.compute("city")
    assert r1 is r2


def test_invalidate_single_column(engine):
    r1 = engine.compute("city")
    engine.invalidate("city")
    r2 = engine.compute("city")
    assert r1 is not r2


def test_invalidate_all(engine):
    engine.compute("city")
    engine.compute("country")
    engine.invalidate()
    # Should not raise; cache is empty
    r = engine.compute("city")
    assert r is not None


def test_empty_rows():
    eng = ColumnFrequencyEngine(["a"], [])
    result = eng.compute("a")
    assert result.total == 0
    assert result.top(5) == []
