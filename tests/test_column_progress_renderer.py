import pytest
from csvlens.column_progress_engine import ColumnProgressEngine
from csvlens.column_progress_renderer import ColumnProgressRenderer


@pytest.fixture
def rows():
    return [
        {"score": "80", "age": "25"},
        {"score": "100", "age": "40"},
        {"score": "50", "age": "10"},
    ]


@pytest.fixture
def engine(rows):
    return ColumnProgressEngine(["score", "age"], rows)


@pytest.fixture
def renderer(engine):
    return ColumnProgressRenderer(engine, col_width=20, bar_width=8)


def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError, match="col_width"):
        ColumnProgressRenderer(engine, col_width=3)


def test_invalid_bar_width_raises(engine):
    with pytest.raises(ValueError, match="bar_width"):
        ColumnProgressRenderer(engine, bar_width=1)


def test_col_width_property(renderer):
    assert renderer.col_width == 20


def test_render_header_returns_string(renderer):
    header = renderer.render_header()
    assert isinstance(header, str)


def test_render_header_contains_columns(renderer):
    header = renderer.render_header()
    assert "score" in header
    assert "age" in header


def test_render_row_returns_string(renderer, rows):
    result = renderer.render_row(rows[0])
    assert isinstance(result, str)


def test_render_row_contains_fill_chars(renderer, rows):
    result = renderer.render_row(rows[1])  # score=100 => full bar
    assert "█" in result


def test_render_row_contains_empty_chars_for_partial(renderer, rows):
    result = renderer.render_row(rows[2])  # score=50 => half bar
    assert "░" in result


def test_render_all_returns_string(renderer, rows):
    out = renderer.render_all(rows)
    assert isinstance(out, str)
    assert out.count("\n") >= len(rows)
