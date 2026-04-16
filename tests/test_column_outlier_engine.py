import pytest
from csvlens.column_outlier_engine import ColumnOutlierEngine, OutlierResult

HEADERS = ["name", "score", "age"]

ROWS = [
    {"name": "Alice", "score": "10", "age": "25"},
    {"name": "Bob",   "score": "12", "age": "27"},
    {"name": "Carol", "score": "11", "age": "26"},
    {"name": "Dave",  "score": "99", "age": "24"},  # outlier in score
    {"name": "Eve",   "score": "10", "age": "28"},
]


@pytest.fixture
def engine():
    return ColumnOutlierEngine(HEADERS)


def test_empty_headers_raises():
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnOutlierEngine([])


def test_non_positive_threshold_raises():
    with pytest.raises(ValueError, match="z_threshold must be positive"):
        ColumnOutlierEngine(HEADERS, z_threshold=0)


def test_headers_property(engine):
    assert engine.headers == HEADERS


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert engine.headers == HEADERS


def test_z_threshold_property(engine):
    assert engine.z_threshold == 2.0


def test_no_results_before_analyse(engine):
    assert engine.result_for("score") is None


def test_analyse_detects_outlier(engine):
    engine.analyse(ROWS)
    result = engine.result_for("score")
    assert isinstance(result, OutlierResult)
    assert result.count >= 1
    # row index 3 (Dave, score=99) should be flagged
    assert 3 in result.outlier_indices


def test_analyse_no_outlier_in_age(engine):
    engine.analyse(ROWS)
    result = engine.result_for("age")
    # ages are tightly clustered; may be None or empty
    if result is not None:
        assert result.count == 0


def test_outlier_columns(engine):
    engine.analyse(ROWS)
    cols = engine.outlier_columns()
    assert "score" in cols


def test_non_numeric_column_skipped(engine):
    engine.analyse(ROWS)
    result = engine.result_for("name")
    assert result is None


def test_unknown_column_raises(engine):
    with pytest.raises(KeyError, match="Unknown column"):
        engine.result_for("nonexistent")


def test_all_same_values_skipped():
    rows = [{"val": "5"} for _ in range(5)]
    eng = ColumnOutlierEngine(["val"])
    eng.analyse(rows)
    assert eng.result_for("val") is None


def test_custom_threshold():
    eng = ColumnOutlierEngine(["score"], z_threshold=0.5)
    eng.analyse(ROWS)
    result = eng.result_for("score")
    assert result is not None
    assert result.count >= 1
