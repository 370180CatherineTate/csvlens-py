import pytest
from csvlens.column_rating_engine import ColumnRatingEngine
from csvlens.column_rating_renderer import ColumnRatingRenderer


@pytest.fixture
def engine():
    e = ColumnRatingEngine(["alpha", "beta", "gamma"])
    e.set_rating("alpha", 3)
    e.set_rating("gamma", 5)
    return e


@pytest.fixture
def renderer(engine):
    return ColumnRatingRenderer(engine, col_width=12)


def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError):
        ColumnRatingRenderer(engine, col_width=4)


def test_col_width_property(renderer):
    assert renderer.col_width == 12


def test_render_header_returns_string(renderer):
    assert isinstance(renderer.render_header(), str)


def test_render_header_contains_columns(renderer, engine):
    header = renderer.render_header()
    for h in engine.headers:
        assert h in header


def test_render_ratings_returns_string(renderer):
    assert isinstance(renderer.render_ratings(), str)


def test_render_ratings_contains_stars(renderer):
    line = renderer.render_ratings()
    assert "★" in line


def test_unrated_column_shows_empty_stars(renderer, engine):
    line = renderer.render_ratings()
    assert "☆☆☆☆☆" in line


def test_render_returns_string(renderer):
    assert isinstance(renderer.render(), str)
