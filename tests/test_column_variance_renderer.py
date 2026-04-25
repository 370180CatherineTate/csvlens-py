import pytest
from csvlens.column_variance_engine import ColumnVarianceEngine
from csvlens.column_variance_renderer import ColumnVarianceRenderer


@pytest.fixture
def rows():
    return [
        {"score": "10", "label": "alpha"},
        {"score": "20", "label": "beta"},
        {"score": "30", "label": "gamma"},
    ]


@pytest.fixture
def engine(rows):
    return ColumnVarianceEngine(["score", "label"], rows)


@pytest.fixture
def renderer(engine):
    return ColumnVarianceRenderer(engine)


# ---------------------------------------------------------------------------
# construction guards
# ---------------------------------------------------------------------------

def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError, match="col_width"):
        ColumnVarianceRenderer(engine, col_width=3)


# ---------------------------------------------------------------------------
# properties
# ---------------------------------------------------------------------------

def test_col_width_property(renderer):
    assert renderer.col_width == 14


def test_custom_col_width(engine):
    r = ColumnVarianceRenderer(engine, col_width=20)
    assert r.col_width == 20


# ---------------------------------------------------------------------------
# render_header
# ---------------------------------------------------------------------------

def test_render_header_returns_string(renderer):
    assert isinstance(renderer.render_header(), str)


def test_render_header_contains_columns(renderer):
    h = renderer.render_header()
    assert "Column" in h
    assert "Variance" in h
    assert "Std Dev" in h


# ---------------------------------------------------------------------------
# render_row
# ---------------------------------------------------------------------------

def test_render_row_numeric_returns_string(renderer):
    assert isinstance(renderer.render_row("score"), str)


def test_render_row_non_numeric_shows_na(renderer):
    row = renderer.render_row("label")
    assert "N/A" in row


def test_render_row_numeric_no_na(renderer):
    row = renderer.render_row("score")
    # strip ANSI codes for assertion
    import re
    clean = re.sub(r"\033\[[0-9;]*m", "", row)
    assert "N/A" not in clean


# ---------------------------------------------------------------------------
# render (full table)
# ---------------------------------------------------------------------------

def test_render_returns_string(renderer):
    assert isinstance(renderer.render(), str)


def test_render_contains_all_columns(renderer):
    output = renderer.render()
    assert "score" in output
    assert "label" in output


def test_render_line_count(renderer):
    # header + one line per column
    lines = renderer.render().split("\n")
    assert len(lines) == 3  # header + score + label
