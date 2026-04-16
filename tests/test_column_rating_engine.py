import pytest
from csvlens.column_rating_engine import ColumnRatingEngine


@pytest.fixture
def engine():
    return ColumnRatingEngine(["name", "age", "score"])


def test_empty_headers_raises():
    with pytest.raises(ValueError):
        ColumnRatingEngine([])


def test_headers_property(engine):
    assert engine.headers == ["name", "age", "score"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


def test_initial_no_ratings(engine):
    assert engine.ratings == {}


def test_set_rating(engine):
    engine.set_rating("age", 4)
    assert engine.get_rating("age") == 4


def test_set_rating_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.set_rating("unknown", 3)


def test_set_rating_out_of_range_raises(engine):
    with pytest.raises(ValueError):
        engine.set_rating("age", 0)
    with pytest.raises(ValueError):
        engine.set_rating("age", 6)


def test_get_rating_unset_returns_none(engine):
    assert engine.get_rating("name") is None


def test_get_rating_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.get_rating("ghost")


def test_clear_rating(engine):
    engine.set_rating("score", 5)
    engine.clear_rating("score")
    assert engine.get_rating("score") is None


def test_clear_rating_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.clear_rating("ghost")


def test_columns_with_min_rating(engine):
    engine.set_rating("name", 2)
    engine.set_rating("age", 4)
    engine.set_rating("score", 5)
    result = engine.columns_with_min_rating(4)
    assert set(result) == {"age", "score"}


def test_clear_all(engine):
    engine.set_rating("name", 3)
    engine.set_rating("age", 1)
    engine.clear_all()
    assert engine.ratings == {}
