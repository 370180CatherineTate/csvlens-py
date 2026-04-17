import pytest
from csvlens.column_bookmark_engine import ColumnBookmarkEngine
from csvlens.column_bookmark_renderer import ColumnBookmarkRenderer


@pytest.fixture
def engine():
    return ColumnBookmarkEngine(["id", "name", "score"])


@pytest.fixture
def renderer(engine):
    return ColumnBookmarkRenderer(engine, col_width=10)


def test_invalid_col_width_raises(engine):
    with pytest.raises(ValueError):
        ColumnBookmarkRenderer(engine, col_width=2)


def test_col_width_property(renderer):
    assert renderer.col_width == 10


def test_render_header_returns_string(renderer):
    result = renderer.render_header()
    assert isinstance(result, str)


def test_render_header_contains_all_columns(renderer, engine):
    result = renderer.render_header()
    for h in engine.headers:
        assert h in result


def test_render_header_shows_empty_star_by_default(renderer):
    result = renderer.render_header()
    assert "\u2606" in result


def test_render_header_shows_filled_star_when_bookmarked(renderer, engine):
    engine.add("name")
    result = renderer.render_header()
    assert "\u2605" in result


def test_render_summary_no_bookmarks(renderer):
    result = renderer.render_summary()
    assert "No bookmarked" in result


def test_render_summary_lists_bookmarked(renderer, engine):
    engine.add("score")
    result = renderer.render_summary()
    assert "score" in result
    assert "Bookmarked" in result
