import pytest
from csvlens.column_tag_engine import ColumnTagEngine


@pytest.fixture
def engine():
    return ColumnTagEngine(["name", "age", "email"])


def test_empty_headers_raises():
    with pytest.raises(ValueError):
        ColumnTagEngine([])


def test_headers_property(engine):
    assert engine.headers == ["name", "age", "email"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("x")
    assert "x" not in engine.headers


def test_initial_no_tags(engine):
    for col in engine.headers:
        assert engine.tags[col] == []


def test_add_tag(engine):
    engine.add_tag("name", "pii")
    assert "pii" in engine.tags["name"]


def test_add_tag_blank_raises(engine):
    with pytest.raises(ValueError):
        engine.add_tag("name", "   ")


def test_add_tag_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.add_tag("nonexistent", "tag")


def test_remove_tag(engine):
    engine.add_tag("age", "numeric")
    engine.remove_tag("age", "numeric")
    assert "numeric" not in engine.tags["age"]


def test_remove_nonexistent_tag_silent(engine):
    engine.remove_tag("age", "ghost")  # should not raise


def test_clear_tags(engine):
    engine.add_tag("email", "pii")
    engine.add_tag("email", "contact")
    engine.clear_tags("email")
    assert engine.tags["email"] == []


def test_columns_with_tag(engine):
    engine.add_tag("name", "pii")
    engine.add_tag("email", "pii")
    result = engine.columns_with_tag("pii")
    assert set(result) == {"name", "email"}


def test_columns_with_tag_none_match(engine):
    assert engine.columns_with_tag("rare") == []


def test_all_tags(engine):
    engine.add_tag("name", "pii")
    engine.add_tag("age", "numeric")
    assert engine.all_tags() == ["numeric", "pii"]


def test_tags_sorted(engine):
    engine.add_tag("name", "z-tag")
    engine.add_tag("name", "a-tag")
    assert engine.tags["name"] == ["a-tag", "z-tag"]
