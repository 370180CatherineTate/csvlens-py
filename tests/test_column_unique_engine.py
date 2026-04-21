"""Tests for ColumnUniqueEngine."""
import pytest

from csvlens.column_unique_engine import ColumnUniqueEngine, UniqueResult


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def rows():
    return [
        {"name": "Alice", "dept": "Eng", "score": "90"},
        {"name": "Bob", "dept": "HR", "score": "80"},
        {"name": "Alice", "dept": "Eng", "score": "70"},
        {"name": "Carol", "dept": "HR", "score": "90"},
        {"name": "Dave", "dept": "Eng", "score": "85"},
    ]


@pytest.fixture()
def engine(rows):
    return ColumnUniqueEngine(["name", "dept", "score"], rows)


# ---------------------------------------------------------------------------
# construction guards
# ---------------------------------------------------------------------------


def test_empty_headers_raises(rows):
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnUniqueEngine([], rows)


def test_sample_size_too_small_raises(rows):
    with pytest.raises(ValueError, match="sample_size must be at least 1"):
        ColumnUniqueEngine(["name"], rows, sample_size=0)


# ---------------------------------------------------------------------------
# headers property
# ---------------------------------------------------------------------------


def test_headers_property(engine):
    assert engine.headers == ["name", "dept", "score"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert engine.headers == ["name", "dept", "score"]


# ---------------------------------------------------------------------------
# results property
# ---------------------------------------------------------------------------


def test_results_keys(engine):
    assert set(engine.results.keys()) == {"name", "dept", "score"}


def test_results_returns_copy(engine):
    r = engine.results
    r["phantom"] = None  # type: ignore[assignment]
    assert "phantom" not in engine.results


# ---------------------------------------------------------------------------
# UniqueResult values
# ---------------------------------------------------------------------------


def test_unique_count_name(engine):
    result = engine.get("name")
    # Alice appears twice but is still one unique value
    assert result.unique_count == 4


def test_unique_count_dept(engine):
    result = engine.get("dept")
    assert result.unique_count == 2


def test_total_equals_row_count(engine):
    for col in ["name", "dept", "score"]:
        assert engine.get(col).total == 5


def test_uniqueness_ratio_dept(engine):
    result = engine.get("dept")
    assert result.uniqueness_ratio == pytest.approx(2 / 5)


def test_is_key_candidate_name(engine):
    # name has 4 unique values out of 5 rows → not a key candidate
    assert engine.get("name").is_key_candidate is False


def test_is_key_candidate_all_unique():
    rows = [
        {"id": "1"},
        {"id": "2"},
        {"id": "3"},
    ]
    eng = ColumnUniqueEngine(["id"], rows)
    assert eng.get("id").is_key_candidate is True


def test_sample_values_capped(rows):
    eng = ColumnUniqueEngine(["name", "dept", "score"], rows, sample_size=2)
    result = eng.get("name")
    assert len(result.sample_values) <= 2


def test_summary_string(engine):
    s = engine.get("dept").summary()
    assert "dept" in s
    assert "2/5" in s


# ---------------------------------------------------------------------------
# get() error handling
# ---------------------------------------------------------------------------


def test_get_unknown_column_raises(engine):
    with pytest.raises(KeyError, match="Unknown column"):
        engine.get("nonexistent")


# ---------------------------------------------------------------------------
# edge cases
# ---------------------------------------------------------------------------


def test_empty_rows():
    eng = ColumnUniqueEngine(["col"], [])
    result = eng.get("col")
    assert result.total == 0
    assert result.unique_count == 0
    assert result.uniqueness_ratio == 0.0
    assert result.is_key_candidate is False


def test_single_row():
    eng = ColumnUniqueEngine(["x"], [{"x": "only"}])
    result = eng.get("x")
    assert result.unique_count == 1
    assert result.is_key_candidate is True
