import pytest

from csvlens.column_correlation_engine import ColumnCorrelationEngine
from csvlens.column_correlation_renderer import ColumnCorrelationRenderer


ROWS = [
    {"a": "1", "b": "2",  "c": "x"},
    {"a": "2", "b": "4",  "c": "y"},
    {"a": "3", "b": "6",  "c": "z"},
]

HEADERS = ["a", "b", "c"]


@pytest.fixture
def engine():
    return ColumnCorrelationEngine(HEADERS, ROWS)


@pytest.fixture
def renderer(engine):
    return ColumnCorrelationRenderer(engine, col_width=15)


# ---------------------------------------------------------------------------
# construction
# ---------------------------------------------------------------------------

def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError, match="col_width"):
        ColumnCorrelationRenderer(engine, col_width=3)


def test_col_width_property(renderer):
    assert renderer.col_width == 15


# ---------------------------------------------------------------------------
# render_header
# ---------------------------------------------------------------------------

def test_render_header_returns_string(renderer):
    assert isinstance(renderer.render_header(), str)


def test_render_header_contains_column_labels(renderer):
    header = renderer.render_header()
    assert "Column A" in header
    assert "Column B" in header
    assert "Strength" in header


# ---------------------------------------------------------------------------
# render_result
# ---------------------------------------------------------------------------

def test_render_result_returns_string(renderer, engine):
    result = engine.compute("a", "b")
    assert isinstance(renderer.render_result(result), str)


def test_render_result_contains_r_value(renderer, engine):
    result = engine.compute("a", "b")
    rendered = renderer.render_result(result)
    assert "1.0000" in rendered


def test_render_result_na_for_non_numeric(renderer, engine):
    result = engine.compute("a", "c")
    rendered = renderer.render_result(result)
    assert "n/a" in rendered


# ---------------------------------------------------------------------------
# render (combined)
# ---------------------------------------------------------------------------

def test_render_returns_string(renderer):
    assert isinstance(renderer.render("a", "b"), str)


def test_render_has_two_lines(renderer):
    output = renderer.render("a", "b")
    lines = output.split("\n")
    assert len(lines) == 2


def test_render_unknown_column_raises(renderer):
    with pytest.raises(KeyError):
        renderer.render("a", "missing")
