import pytest
from csvlens.column_sample_engine import ColumnSampleEngine, SampleResult


HEADERS = ["name", "age", "city"]
ROWS = [
    {"name": "Alice", "age": "30", "city": "London"},
    {"name": "Bob", "age": "25", "city": "Paris"},
    {"name": "Carol", "age": "35", "city": "Berlin"},
    {"name": "Dave", "age": "28", "city": "Tokyo"},
    {"name": "Eve", "age": "22", "city": "Sydney"},
]


@pytest.fixture
def engine():
    return ColumnSampleEngine(HEADERS, ROWS, sample_size=3, seed=42)


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnSampleEngine([], ROWS)


def test_sample_size_too_small_raises():
    with pytest.raises(ValueError, match="sample_size must be at least 1"):
        ColumnSampleEngine(HEADERS, ROWS, sample_size=0)


def test_headers_property(engine):
    assert engine.headers == HEADERS


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert engine.headers == HEADERS


def test_sample_size_property(engine):
    assert engine.sample_size == 3


def test_results_keys(engine):
    assert set(engine.results.keys()) == set(HEADERS)


def test_get_returns_sample_result(engine):
    result = engine.get("name")
    assert isinstance(result, SampleResult)
    assert result.column == "name"


def test_get_unknown_column_raises(engine):
    with pytest.raises(KeyError, match="Unknown column"):
        engine.get("nonexistent")


def test_sample_count_respects_sample_size(engine):
    for col in HEADERS:
        assert engine.get(col).count == 3


def test_sample_values_are_from_rows(engine):
    all_names = {r["name"] for r in ROWS}
    for v in engine.get("name").values:
        assert v in all_names


def test_seed_produces_deterministic_results():
    e1 = ColumnSampleEngine(HEADERS, ROWS, sample_size=3, seed=7)
    e2 = ColumnSampleEngine(HEADERS, ROWS, sample_size=3, seed=7)
    assert e1.get("name").values == e2.get("name").values


def test_different_seeds_may_differ():
    e1 = ColumnSampleEngine(HEADERS, ROWS, sample_size=3, seed=1)
    e2 = ColumnSampleEngine(HEADERS, ROWS, sample_size=3, seed=99)
    # With enough rows the samples may differ; just check they run
    assert e1.get("name").count == e2.get("name").count


def test_sample_size_larger_than_rows_clamps():
    engine = ColumnSampleEngine(HEADERS, ROWS, sample_size=100, seed=0)
    assert engine.get("city").count == len(ROWS)


def test_resample_changes_seed(engine):
    before = engine.get("age").values[:]
    engine.resample(seed=999)
    after = engine.get("age").values
    # Values are still valid
    all_ages = {r["age"] for r in ROWS}
    for v in after:
        assert v in all_ages
    assert engine._seed == 999


def test_summary_string(engine):
    s = engine.get("name").summary()
    assert "name" in s
    assert "samples" in s


def test_empty_rows_gives_empty_samples():
    engine = ColumnSampleEngine(HEADERS, [], sample_size=3, seed=0)
    for col in HEADERS:
        assert engine.get(col).count == 0
