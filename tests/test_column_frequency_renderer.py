import pytest

from csvlens.column_frequency_engine import ColumnFrequencyEngine
from csvlens.column_frequency_renderer import ColumnFrequencyRenderer


ROWS = [
    {"city": "London", "country": "UK"},
    {"city": "Paris", "country": "FR"},
    {"city": "London", "country": "UK"},
    {"city": "Berlin", "country": "DE"},
]
HEADERS = ["city", "country"]


@pytest.fixture
def engine():
    return ColumnFrequencyEngine(HEADERS, ROWS)


@pytest.fixture
def renderer(engine):
    return ColumnFrequencyRenderer(engine, col_width=15, top_n=5)


def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError, match="col_width must be at least 4"):
        ColumnFrequencyRenderer(engine, col_width=3)


def test_invalid_top_n_raises(engine):
    with pytest.raises(ValueError, match="top_n must be at least 1"):
        ColumnFrequencyRenderer(engine, top_n=0)


def test_col_width_property(renderer):
    assert renderer.col_width == 15


def test_render_returns_string(renderer):
    output = renderer.render("city")
    assert isinstance(output, str)


def test_render_contains_column_name(renderer):
    output = renderer.render("city")
    assert "city" in output


def test_render_contains_unique_count(renderer):
    output = renderer.render("city")
    assert "3 unique" in output


def test_render_contains_total_rows(renderer):
    output = renderer.render("city")
    assert "4 rows" in output


def test_render_contains_top_value(renderer):
    output = renderer.render("city")
    assert "London" in output


def test_render_long_value_truncated(engine):
    rows = [{"tag": "x" * 50}]
    eng = ColumnFrequencyEngine(["tag"], rows)
    rend = ColumnFrequencyRenderer(eng, col_width=10)
    output = rend.render("tag")
    assert "…" in output


def test_render_multiline(renderer):
    output = renderer.render("city")
    assert "\n" in output
