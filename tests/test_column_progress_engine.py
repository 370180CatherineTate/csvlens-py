import pytest
from csvlens.column_progress_engine import ColumnProgressEngine, _to_float


@pytest.fixture
def rows():
    return [
        {"score": "80", "age": "25", "label": "alpha"},
        {"score": "100", "age": "40", "label": "beta"},
        {"score": "50", "age": "", "label": "gamma"},
    ]


@pytest.fixture
def engine(rows):
    return ColumnProgressEngine(["score", "age", "label"], rows)


def test_to_float_valid():
    assert _to_float("3.14") == pytest.approx(3.14)


def test_to_float_invalid():
    assert _to_float("abc") is None
    assert _to_float("") is None


def test_empty_headers_raises(rows):
    with pytest.raises(ValueError, match="headers must not be empty"):
        ColumnProgressEngine([], rows)


def test_headers_property(engine):
    assert engine.headers == ["score", "age", "label"]


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


def test_effective_max_numeric(engine):
    assert engine.effective_max("score") == pytest.approx(100.0)


def test_effective_max_non_numeric(engine):
    assert engine.effective_max("label") is None


def test_effective_max_partial_nulls(engine):
    assert engine.effective_max("age") == pytest.approx(40.0)


def test_set_max_overrides(engine):
    engine.set_max("score", 200.0)
    assert engine.effective_max("score") == pytest.approx(200.0)


def test_set_max_invalid_column(engine):
    with pytest.raises(KeyError):
        engine.set_max("nonexistent", 100.0)


def test_set_max_non_positive(engine):
    with pytest.raises(ValueError, match="positive"):
        engine.set_max("score", 0)


def test_clear_max_restores_computed(engine):
    engine.set_max("score", 200.0)
    engine.clear_max("score")
    assert engine.effective_max("score") == pytest.approx(100.0)


def test_progress_full(engine):
    assert engine.progress("score", "100") == pytest.approx(1.0)


def test_progress_half(engine):
    assert engine.progress("score", "50") == pytest.approx(0.5)


def test_progress_clamped_above(engine):
    assert engine.progress("score", "200") == pytest.approx(1.0)


def test_progress_clamped_below(engine):
    assert engine.progress("score", "-10") == pytest.approx(0.0)


def test_progress_non_numeric_returns_none(engine):
    assert engine.progress("score", "n/a") is None


def test_progress_no_max_returns_none(engine):
    assert engine.progress("label", "alpha") is None


def test_progress_unknown_column_raises(engine):
    with pytest.raises(KeyError):
        engine.progress("missing", "10")
