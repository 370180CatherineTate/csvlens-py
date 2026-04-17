import pytest
from csvlens.column_index_engine import ColumnIndexEngine

HEADERS = ["id", "name", "city"]

ROWS = [
    {"id": "1", "name": "Alice", "city": "London"},
    {"id": "2", "name": "Bob",   "city": "Paris"},
    {"id": "3", "name": "Alice", "city": "London"},
    {"id": "4", "name": "Carol", "city": "Berlin"},
]


@pytest.fixture
def engine() -> ColumnIndexEngine:
    return ColumnIndexEngine(HEADERS)


def test_empty_headers_raises():
    with pytest.raises(ValueError):
        ColumnIndexEngine([])


def test_headers_property(engine):
    assert engine.headers == HEADERS


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert engine.headers == HEADERS


def test_initial_no_indexed_columns(engine):
    assert engine.indexed_columns == []


def test_build_invalid_column_raises(engine):
    with pytest.raises(KeyError):
        engine.build("nonexistent", ROWS)


def test_build_adds_to_indexed_columns(engine):
    engine.build("name", ROWS)
    assert "name" in engine.indexed_columns


def test_lookup_before_build_raises(engine):
    with pytest.raises(KeyError):
        engine.lookup("name", "Alice")


def test_lookup_existing_value(engine):
    engine.build("name", ROWS)
    result = engine.lookup("name", "Alice")
    assert sorted(result) == [0, 2]


def test_lookup_missing_value_returns_empty(engine):
    engine.build("name", ROWS)
    assert engine.lookup("name", "Zara") == []


def test_lookup_single_match(engine):
    engine.build("city", ROWS)
    assert engine.lookup("city", "Berlin") == [3]


def test_unique_values_sorted(engine):
    engine.build("city", ROWS)
    assert engine.unique_values("city") == ["Berlin", "London", "Paris"]


def test_unique_values_before_build_raises(engine):
    with pytest.raises(KeyError):
        engine.unique_values("city")


def test_drop_removes_index(engine):
    engine.build("name", ROWS)
    engine.drop("name")
    assert "name" not in engine.indexed_columns


def test_drop_nonexistent_is_noop(engine):
    engine.drop("name")  # should not raise


def test_clear_removes_all(engine):
    engine.build("name", ROWS)
    engine.build("city", ROWS)
    engine.clear()
    assert engine.indexed_columns == []
