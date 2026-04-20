import pytest
from csvlens.column_score_engine import ColumnScoreEngine, _to_float
from csvlens.column_score_renderer import ColumnScoreRenderer


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

HEADERS = ["name", "math", "science", "english"]

ROWS = [
    {"name": "Alice", "math": "90", "science": "80", "english": "70"},
    {"name": "Bob",   "math": "60", "science": "55", "english": "85"},
    {"name": "Carol", "math": "",   "science": "92", "english": "88"},
]


@pytest.fixture
def engine():
    return ColumnScoreEngine(HEADERS)


@pytest.fixture
def renderer(engine):
    return ColumnScoreRenderer(engine, col_width=10)


# ---------------------------------------------------------------------------
# _to_float
# ---------------------------------------------------------------------------

def test_to_float_valid():
    assert _to_float("3.14") == pytest.approx(3.14)


def test_to_float_invalid():
    assert _to_float("abc") is None
    assert _to_float("") is None


# ---------------------------------------------------------------------------
# ColumnScoreEngine
# ---------------------------------------------------------------------------

def test_empty_headers_raises():
    with pytest.raises(ValueError, match="empty"):
        ColumnScoreEngine([])


def test_headers_property(engine):
    assert engine.headers == HEADERS


def test_headers_returns_copy(engine):
    h = engine.headers
    h.append("extra")
    assert "extra" not in engine.headers


def test_initial_no_weights(engine):
    assert engine.weights == {}


def test_set_weight(engine):
    engine.set_weight("math", 2.0)
    assert engine.weights["math"] == 2.0


def test_set_weight_invalid_column_raises(engine):
    with pytest.raises(KeyError):
        engine.set_weight("nonexistent", 1.0)


def test_set_weight_negative_raises(engine):
    with pytest.raises(ValueError, match=">= 0"):
        engine.set_weight("math", -1.0)


def test_score_row_no_weights_returns_none(engine):
    assert engine.score_row(ROWS[0]) is None


def test_score_row_single_weight(engine):
    engine.set_weight("math", 1.0)
    assert engine.score_row(ROWS[0]) == pytest.approx(90.0)


def test_score_row_multiple_weights(engine):
    engine.set_weight("math", 1.0)
    engine.set_weight("science", 2.0)
    # Alice: 90*1 + 80*2 = 250
    assert engine.score_row(ROWS[0]) == pytest.approx(250.0)


def test_score_row_missing_numeric_value(engine):
    engine.set_weight("math", 1.0)
    engine.set_weight("science", 1.0)
    # Carol: math is blank => only science counts => 92
    assert engine.score_row(ROWS[2]) == pytest.approx(92.0)


def test_score_rows_length(engine):
    engine.set_weight("math", 1.0)
    scores = engine.score_rows(ROWS)
    assert len(scores) == len(ROWS)


def test_ranked_descending(engine):
    engine.set_weight("math", 1.0)
    ranked = engine.ranked(ROWS, ascending=False)
    scores = [engine.score_row(r) for r in ranked]
    numeric = [s for s in scores if s is not None]
    assert numeric == sorted(numeric, reverse=True)


def test_ranked_ascending(engine):
    engine.set_weight("math", 1.0)
    ranked = engine.ranked(ROWS, ascending=True)
    scores = [engine.score_row(r) for r in ranked]
    numeric = [s for s in scores if s is not None]
    assert numeric == sorted(numeric)


def test_clear_weight(engine):
    engine.set_weight("math", 1.0)
    engine.clear_weight("math")
    assert "math" not in engine.weights


def test_clear_all(engine):
    engine.set_weight("math", 1.0)
    engine.set_weight("science", 0.5)
    engine.clear_all()
    assert engine.weights == {}


# ---------------------------------------------------------------------------
# ColumnScoreRenderer
# ---------------------------------------------------------------------------

def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError, match=">= 4"):
        ColumnScoreRenderer(engine, col_width=2)


def test_col_width_property(renderer):
    assert renderer.col_width == 10


def test_render_header_returns_string(renderer):
    assert isinstance(renderer.render_header(), str)


def test_render_score_none(renderer):
    result = renderer.render_score(None)
    assert "n/a" in result


def test_render_row_no_weights(engine, renderer):
    result = renderer.render_row(ROWS[0])
    assert "n/a" in result


def test_render_all_includes_header(engine, renderer):
    engine.set_weight("math", 1.0)
    lines = renderer.render_all(ROWS, include_header=True)
    assert len(lines) == len(ROWS) + 1


def test_render_all_no_header(engine, renderer):
    engine.set_weight("math", 1.0)
    lines = renderer.render_all(ROWS, include_header=False)
    assert len(lines) == len(ROWS)
